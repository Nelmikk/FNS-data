import asyncio
import multiprocessing as mp
import warnings
from abc import ABC
from typing import Final, Generator
from pathlib import Path

from zipfile import ZipFile
import time

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from src.database_modules.core import insert_data_async, create_index, rename_tables, drop_temp_table, rename_index
from src.database_modules.orm import drop_tables_from_models, create_tables_from_models
from src.database_modules.database_conf import settings_super_user

from src.models.other_models import Parser_output

from src.fns_modules.fns_downloaders import Downloader_Base
from src.fns_modules.fns_parsers import Parser_Base, Parser_SNO_UL, Parser_SNO_IP, Parser_RSMP_MAIN_INFO, Parser_RSMP_ADDITIONAL_OKVEDS, Parser_RSMP_LICENSES
from src.fns_modules.fns_downloaders import Downloader_RSMP, Downloader_SNR



async def async_generator_wrapper(sync_generator: Generator, ):
    """
    Преобразует синхронный генератор в асинхронный.
    :param sync_generator:
    :return:
    """
    def get_next(generator: Generator):
        try: return next(generator)
        except: return None
    while True:
        item = await asyncio.to_thread(get_next, sync_generator)
        if item is None: break
        yield item

def _run_parse_and_insert(*args,
                          **kwargs, ):
    """
    Просто запускает асинхронный _parse_and_insert.
    :param args:
    :param kwargs:
    :return:
    """
    asyncio.run(_parse_and_insert(*args, **kwargs))


async def _parse_and_insert(parser: type[Parser_Base],
                            file_dir: str | Path,
                            left: int,
                            right: int,
                            semaphore_count: int, ) -> None:
    """
    Аснихронный метод для парсинга данных и занесения их в БД.

        Запускается для каждого потока.
        async_engine создается для каждого потока отдельно и юзается асинхронно.


    :param parser:          Required. Принимает классы типа src.fns_modules.fns_parsers.Base_parser.
                                Класс, который выполняет парсинг данных из zip-архива/xml-файла.
    :param file_dir:        Required. Принимает pathlib.Path | str.
                                Путь к zip-архиву или xml-файлу.
    :param left:            Optional. Принимает int.
                                Левая граница при парсинге zip-архива, те первый файл.

    :param right:           Optional. Принимает int.
                                Правая граница при парсинге zip-архива, те последний файл.
    :return:
    """

    parser = parser()
    parsed_data = parser.parse(file_dir=file_dir,
                               left=left,
                               right=right)

    # Для каждого процесса надо создавать отдельный пул соединений.
    async_engine = create_async_engine(url=settings_super_user.DATABASE_URL_ASYNC,
                                       echo=False,
                                       pool_size=semaphore_count,
                                       pool_pre_ping=True)
    # Семафор для ограничения создания огромного количества соединений.
    semaphore = asyncio.Semaphore(semaphore_count)

    # Асинхронные парсинг и вставка данных в БД.
    print(f'{left = } || {right = }')
    l = 0
    r = right - left
    ts = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        async for org_data in async_generator_wrapper(parsed_data):
            if org_data is None:
                continue
            await semaphore.acquire()
            tg.create_task(_insert_data(async_engine=async_engine,
                                        data=org_data,
                                        semaphore=semaphore))
            l += 1
            print(f'\r{time.perf_counter()-ts} || {l}/{r}', end='', flush=True)
    # Закрытие пула соединений.
    await async_engine.dispose()


async def _insert_data(async_engine: AsyncEngine,
                       data: Parser_output,
                       semaphore: asyncio.Semaphore, ) -> None:
        """
        Занесение данных в БД.

        :param async_engine:
        :param data:
        :return:
        """
        if not data['data']:
            print('No data from file')
            return
        try:
            async with semaphore:
                await insert_data_async(tablename=data['tablename'], values=data['data'], engine=async_engine)
        finally:
            semaphore.release()


class Base_FNS_data_updater(ABC):
    """
    Класс для скачивания, парсинга и занесения в БД всех спаршенных данных.
        1. Класс наследуется и от наследника создается экземпляр.
        2. Экземпляр вызывается только .update_data() со всеми необходимыми аргументами.
        3. Скачивается zip-архив и объявляется file_dir, если не передан file_dir.
        4. Создается _cpu_count процессов, которые разделяются на
    """
    # Базовое значение кол-ва процессов
    __cpu_count_base: Final = 1
    # Базовоное значение кол-ва активных корутин
    __semaphore_count: Final = 2

    # Класс для скачивания документов, в __init__ создается экземпляр.
    #   Не задается и не изменяется после инициилизации.
    _downloader: Downloader_Base

    # Класс для парсинга данных, экземпляры создаются отдельно для каждого процесса.
    #   Не задается и не изменяется после инициилизации.
    _parser: type[Parser_Base]

    # Количество процессов для парсинга и занесения в БД.
    #   Задается во время инициилизации.
    _cpu_count: int

    # Количество создаваемых корутин внутри отдельных процессов.
    #   Задается во время инициилизации.
    _semaphore_count: int


    def __init__(self,
                 cpu_count: int = 1,
                 semaphore_count: int = 2,):
        """
        Инициализация экземпляра, проверка на допустимость количества процессов.

            cpu_count принимает базовое значение, если заданный cpu_count больше макс. кол-ва логических процессоров
            или меньше или равен 0.

        :param semaphore_count:             Optional.Принимает int.
                                                Ограничение количества создаваемых корутин.

        :param cpu_count:                   Optional. принимает int.
                                                Количество создаваемых процессов.
                                                 Не позволит создать больше, чем есть на машине.
        """
        print(f'\n\n{self.__class__.__name__} is updating data\n')
        self._semaphore_count = semaphore_count if semaphore_count > 0 else self.__semaphore_count
        if not (0 < cpu_count <= mp.cpu_count()):
            warnings.warn('The argument "cpu_count" is set to base value: 1')
            self._cpu_count = self.__cpu_count_base
        else:
            self._cpu_count = cpu_count


    @property
    def semaphore_count(self, ):
        return self._semaphore_count

    @semaphore_count.setter
    def semaphore_count(self, val: int ):
        self._semaphore_count = val if val > 0 else self._semaphore_count


    @property
    def cpu_count(self, ):
        return self._cpu_count

    @cpu_count.setter
    def cpu_count(self, val: int, ):
        self._cpu_count = val if mp.cpu_count() >= val > 0 else self._cpu_count


    def update_data(self,
                    file_dir: Path | str,
                    delete_file_after_update: bool = True,
                    reset_table: bool = True,
                    rewrite_table: bool = False, ) -> None:
        """
        Запуск апдейта данных.

        :param reset_table:                     bool.
                                                    Если True, то shadow таблица создается заново перед парсингом.

        :param rewrite_table:                   bool.
                                                    Если True, то таблица, в которую записываются данные, перезапишет
                                                    основную таблицу для хранения данных.

        :param delete_file_after_update:        bool.
                                                    Если True, то файл, передаваемый в file_dir удаляется после аптейта.

        :param file_dir:                        pathlib.Path | str.
                                                    Полный путь к zip-архиву.
                                                    Если str, то потом конвертирует в Path.

        :return:
        """
        if isinstance(file_dir, str):
            file_dir = Path(file_dir)
        # elif file_dir is None:
        #     print(f'{self.__class__.__name__} is downloading zip-file')
        #     file_dir = self.download()
        # # Если ошибка во время скачивания, то вернет None.
        # if file_dir is None:
        #     return

        if reset_table: self._reset_table()

        xml_files_num = _xml_files_num(zip_file_dir=file_dir)
        self._create_processes(xml_files_num=xml_files_num,
                               file_dir=file_dir, )

        if delete_file_after_update: Path(fr'{file_dir}').unlink(missing_ok=True)

        if rewrite_table:
            self._set_indexes()

            self._replace_tables()

            self._drop_temp_table()

            self._rename_index()
        return


    def download(self, ) -> Path | None:
        """
        Скачивание самого актуального zip-архива.
            Возвращает None, если не получилось скачать, иначе возвращает pathlib.Path скачанного zip-архива.
        :return:
        """
        print('Downloading zip-archive...\n')
        file_dir = self._downloader.download()
        return file_dir


    def _create_processes(self,
                          xml_files_num: int,
                          file_dir: Path, ):
        """
        Запуск нескольких процессов для парсинга и занесения данныхв БД.

            Данные распределяются +- равномерно по процессам.
        :param xml_files_num:
        :param file_dir:
        :return:
        """
        processes = []
        for i in range(self._cpu_count):
            left = int(xml_files_num / self._cpu_count) * i
            right = int(xml_files_num / self._cpu_count) * (i + 1) if i != self._cpu_count - 1 else xml_files_num
            if right > xml_files_num: right = xml_files_num
            processes.append(mp.Process(
                target=_run_parse_and_insert,
                args=(self._parser, file_dir,left, right, self._semaphore_count)
            ))

        for process in processes:
            process.start()

        for process in processes:
            process.join()
        ...

    def _reset_table(self, ):
        drop_tables_from_models(tables_models=[self._parser.tag_parser._database_model])
        create_tables_from_models(tables_models=[self._parser.tag_parser._database_model,
                                                 self._parser.tag_parser._database_model.non_shadow_table])
        ...

    def _set_indexes(self, ):
        for index_item in self._parser.tag_parser._database_model.DB_indexes:
            create_index(index_name=index_item['index_name'],
                         column_index=index_item['column_index'],
                         table=self._parser.tag_parser._database_model,
                         index_type=index_item['index_type'])
            ...

    def _replace_tables(self, ):
        rename_tables(new_tablename=self._parser.tag_parser._database_model.__tablename__,
                      old_tablename=self._parser.tag_parser._database_model.non_shadow_table.__tablename__)

    def _drop_temp_table(self, ):
        drop_temp_table(tablename=self._parser.tag_parser._database_model.non_shadow_table.__tablename__)
        ...

    def _rename_index(self, ):
        for index_item in self._parser.tag_parser._database_model.DB_indexes:
            old_index_name = index_item['index_name']
            new_index_name = [i['index_name'] for i in self._parser.tag_parser._database_model.non_shadow_table.DB_indexes
                              if i['column_index'] == index_item['column_index']][0]
            rename_index(old_index_name=old_index_name, new_index_name=new_index_name)

def _xml_files_num(zip_file_dir: Path, ) -> int:
    """
    Возвращает количество файлов в zip-архиве.
    :param zip_file_dir:
    :return:
    """
    with ZipFile(zip_file_dir) as zf:
        xml_files_num = len(zf.namelist())
    return xml_files_num


class FNS_data_updater_RSMP_MAIN_INFO(Base_FNS_data_updater):
    """
    Дочерний класс Base_FNS_data_updater.
        Изменены параметры парсера и скачивающего класса, логика работы та же.
    """
    def __init__(self,
                 cpu_count: int = 1,
                 semaphore_count: int = 2,):
        self._downloader = Downloader_RSMP()
        self._parser = Parser_RSMP_MAIN_INFO
        super().__init__(cpu_count=cpu_count,
                         semaphore_count=semaphore_count)



class FNS_data_updater_RSMP_ADDITIONAL_OKVEDS(Base_FNS_data_updater):
    """
    Дочерний класс Base_FNS_data_updater.
        Изменены параметры парсера и скачивающего класса, логика работы та же.
    """
    def __init__(self,
                 cpu_count: int = 1,
                 semaphore_count: int = 2, ):
        self._downloader = Downloader_RSMP()
        self._parser = Parser_RSMP_ADDITIONAL_OKVEDS
        super().__init__(cpu_count=cpu_count,
                         semaphore_count=semaphore_count)


class FNS_data_updater_LICENSES(Base_FNS_data_updater):
    """
    Дочерний класс Base_FNS_data_updater.
        Изменены параметры парсера и скачивающего класса, логика работы та же.
    """
    def __init__(self, cpu_count: int = 1,
                 semaphore_count: int = 2,):
        self._downloader = Downloader_RSMP()
        self._parser = Parser_RSMP_LICENSES
        super().__init__(cpu_count=cpu_count,
                         semaphore_count=semaphore_count)

class FNS_data_updater_SNO(Base_FNS_data_updater):
    """
    Дочерний класс Base_FNS_data_updater.
        Изменены параметры парсера и скачивающего класса, логика работы та же.
    """
    def __init__(self,
                 cpu_count: int = 1,
                 semaphore_count: int = 2,):
        self._downloader = Downloader_SNR()
        self._parser = Parser_SNO_UL
        super().__init__(cpu_count=cpu_count,
                         semaphore_count=semaphore_count)



class FNS_data_updater_SNO_IP(Base_FNS_data_updater):
    """
    Дочерний класс Base_FNS_data_updater.
        Изменены параметры парсера и скачивающего класса, логика работы та же.
    """
    def __init__(self,
                 cpu_count: int = 1,
                 semaphore_count: int = 2, ):
        self._downloader = Downloader_SNR()
        self._parser = Parser_SNO_IP
        super().__init__(cpu_count=cpu_count,
                         semaphore_count=semaphore_count)

