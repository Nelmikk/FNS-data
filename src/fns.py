import asyncio
import multiprocessing as mp
from abc import ABC
from typing import Final
from pathlib import Path
from zipfile import ZipFile
import time
import logging

from src.database_modules.database_sessions import (get_async_engine_super_user,
                                                    get_sync_engine_super_user,
                                                    get_sessionmaker)
from src.database_modules.insert_queries.queries import *
from src.database_modules.metadata_queries.queries import  *

from src.database_modules.database_conf import settings_super_user

from src.models.other_models import Parser_output

from src.fns_modules.fns_config import fns_settings
from src.fns_modules.fns_downloaders import DownloaderBase, DownloaderSNRIP
from src.fns_modules.fns_parsers import ParserBase, ParserSNOUL, ParserSNOIP, ParserMainInfo, ParserAdditionalOkveds, ParserLicenses
from src.fns_modules.fns_downloaders import DownloaderRSMP, DownloaderSNRUL

mp.set_start_method('spawn', force=True)


def _run_parse_and_insert(*args,
                          **kwargs, ):
    """
    Просто запускает асинхронный _parse_and_insert.
    :param args:
    :param kwargs:
    :return:
    """
    asyncio.run(_parse_and_insert(*args, **kwargs))


async def _parse_and_insert(parser: type[ParserBase],
                            file_dir: str | Path,
                            log_filename: str,
                            left: int = 0,
                            right: int = 1,
                            semaphore_count: int = 1, ) -> None:
    """
    Аснихронная функция для парсинга данных и занесения их в БД.

        Запускается для каждого процесса.
        async_engine создается для каждого процесса отдельно.


    :param parser:          Обязательный параметр. Принимает классы типа src.fns_modules.fns_parsers.Base_parser.
                                Класс, который выполняет парсинг данных из zip-архива/xml-файла.

    :param file_dir:        Обязательный параметр. Принимает pathlib.Path | str.
                                Путь к zip-архиву или xml-файлу.

    :param left:            Необязательный параметр. Принимает int.
                                Левая граница при парсинге zip-архива, те первый файл.

    :param right:           Необязательный параметр. Принимает int.
                                Правая граница при парсинге zip-архива, те последний файл.
    :return:
    """

    parser = parser(log_filename=log_filename)
    parsed_data = parser.parse(file_dir=file_dir,
                               left=left,
                               right=right,)

    # Для каждого процесса надо создавать отдельный пул соединений.
    async_engine = get_async_engine_super_user(url=settings_super_user.DATABASE_URL_ASYNC,
                                               echo=False,
                                               pool_size=semaphore_count,
                                               pool_pre_ping=True)
    # Семафор для ограничения создания огромного количества соединений.
    semaphore = asyncio.Semaphore(semaphore_count)
    try:
        # Асинхронные парсинг и вставка данных в БД.
        logging.info(f'\n{left = } || {right = }')
        l = 0
        r = right - left
        ts = time.perf_counter()
        async with asyncio.TaskGroup() as tg:
            async for org_data in parsed_data:
                if org_data is None:
                    continue
                if not org_data['data']:
                    continue
                await semaphore.acquire()
                tg.create_task(_insert_data(async_engine=async_engine,
                                            data=org_data,
                                            semaphore=semaphore))
                l += 1
                print(f'\r{time.perf_counter()-ts} || {l}/{r}', end='', flush=True)
        # Закрытие пула соединений.
    finally:
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
        try:
            await insert_data_async(tablename=data['tablename'], values=data['data'], engine=async_engine)
        finally:
            semaphore.release()


class BaseFNSDataUpdater(ABC):
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
    __semaphore_count_base: Final = 2

    # Класс для скачивания документов, в __init__ создается экземпляр.
    #   Не задается и не изменяется после инициилизации.
    _downloader: DownloaderBase

    # Класс для парсинга данных, экземпляры создаются отдельно для каждого процесса.
    #   Не задается и не изменяется после инициилизации.
    _parser: type[ParserBase]

    # Количество процессов для парсинга и занесения в БД.
    #   Задается во время инициилизации.
    _cpu_count: int

    # Количество создаваемых корутин внутри отдельных процессов.
    #   Задается во время инициилизации.
    _semaphore_count: int


    def __init__(self,
                 cpu_count: int = 1,
                 semaphore_count: int = 2, ):
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
        logging.basicConfig(level=logging.WARNING, filename='fns_log.log',
                            filemode='w', format='%(asctime)s %(levelname)s %(message)s')
        self._semaphore_count = semaphore_count if semaphore_count > 0 else self.__semaphore_count_base

        if semaphore_count <= 0:
            logging.warning(f'The parameter "_semaphore_count" is set to base value: {self.__semaphore_count_base}')
            self._semaphore_count = self.__semaphore_count_base
        else:
            self._semaphore_count = semaphore_count

        if not (0 < cpu_count <= mp.cpu_count()):
            logging.warning(f'The parameter "_cpu_count" is set to base value: {self.__cpu_count_base}')
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
        print(f'\n\n{self.__class__.__name__} is updating data\n')

        self.engine = get_sync_engine_super_user(pool_size=1, max_overflow=1)
        self.sessionmaker = get_sessionmaker(sync_engine=self.engine)

        try:
            if file_dir is None:
                logging.error('"file_dir" parameter was given with None value.')
                return

            if isinstance(file_dir, str):
                file_dir = Path(file_dir)

            if reset_table:
                self._reset_table()

            if str(file_dir).endswith('.zip'):
                xml_files_num = _xml_files_num(zip_file_dir=file_dir)
                self._create_processes(xml_files_num=xml_files_num,
                                       file_dir=file_dir, )
            elif str(file_dir).endswith('.xml'):
                _run_parse_and_insert(parser=self._parser, file_dir=file_dir, semaphore_count=self._semaphore_count)

            if delete_file_after_update: Path(fr'{file_dir}').unlink(missing_ok=True)

            if rewrite_table:
                self._set_indexes()

                self._replace_tables()

                self._drop_temp_table()

                self._rename_index()
        except Exception as e:
            logging.error(msg='Unexpected error occurred', exc_info=True)

        finally:
            self.engine.dispose()


    def download(self, ) -> Path | None:
        """
        Скачивание самого актуального zip-архива.
            Возвращает None, если не получилось скачать, иначе возвращает pathlib.Path скачанного zip-архива.
        :return:
        """
        logging.info('Downloading zip-archive...\n')
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
                kwargs={'parser': self._parser,
                        'file_dir': file_dir,
                        'left': left,
                        'right': right,
                        'semaphore_count': self._semaphore_count,
                        'log_filename': f'fns_log_process{i}.log', }))

        for process in processes:
            process.start()

        for process in processes:
            process.join()
        ...

    def _reset_table(self, ):
        drop_tables_from_models(tables_models=[self._parser.tag_parser._database_model],
                                session=self.sessionmaker, )
        create_tables_from_models(tables_models=[self._parser.tag_parser._database_model,
                                                 self._parser.tag_parser._database_model.non_shadow_table],
                                  session=self.sessionmaker, )
        ...

    def _set_indexes(self, ):
        for index_item in self._parser.tag_parser._database_model.DB_indexes:
            create_index(engine=self.engine,
                         index_name=index_item['index_name'],
                         column_index=index_item['column_index'],
                         table=self._parser.tag_parser._database_model,
                         index_type=index_item['index_type'], )
            ...

    def _replace_tables(self, ):
        rename_tables(engine=self.engine,
                      new_tablename=self._parser.tag_parser._database_model.__tablename__,
                      old_tablename=self._parser.tag_parser._database_model.non_shadow_table.__tablename__,)

    def _drop_temp_table(self, ):
        drop_temp_table(engine=self.engine,
                        tablename=self._parser.tag_parser._database_model.non_shadow_table.__tablename__)
        ...

    def _rename_index(self, ):
        for index_item in self._parser.tag_parser._database_model.DB_indexes:
            old_index_name = index_item['index_name']
            new_index_name = [i['index_name'] for i in self._parser.tag_parser._database_model.non_shadow_table.DB_indexes
                              if i['column_index'] == index_item['column_index']][0]
            rename_index(old_index_name=old_index_name,
                         new_index_name=new_index_name,
                         engine=self.engine)

def _xml_files_num(zip_file_dir: Path, ) -> int:
    """
    Возвращает количество файлов в zip-архиве.
    :param zip_file_dir:
    :return:
    """
    with ZipFile(zip_file_dir) as zf:
        xml_files_num = len(zf.namelist())
    return xml_files_num


class UpdaterMainInfo(BaseFNSDataUpdater):
    """
    Дочерний класс Base_FNS_data_updater.
        Изменены параметры парсера и скачивающего класса, логика работы та же.
    """
    def __init__(self,
                 cpu_count: int = 1,
                 semaphore_count: int = 2,):
        self._downloader = DownloaderRSMP()
        self._parser = ParserMainInfo
        super().__init__(cpu_count=cpu_count,
                         semaphore_count=semaphore_count)



class UpdaterAdditionalOkveds(BaseFNSDataUpdater):
    """
    Дочерний класс Base_FNS_data_updater.
        Изменены параметры парсера и скачивающего класса, логика работы та же.
    """
    def __init__(self,
                 cpu_count: int = 1,
                 semaphore_count: int = 2, ):
        self._downloader = DownloaderRSMP()
        self._parser = ParserAdditionalOkveds
        super().__init__(cpu_count=cpu_count,
                         semaphore_count=semaphore_count)


class UpdaterLicenses(BaseFNSDataUpdater):
    """
    Дочерний класс Base_FNS_data_updater.
        Изменены параметры парсера и скачивающего класса, логика работы та же.
    """
    def __init__(self, cpu_count: int = 1,
                 semaphore_count: int = 2,):
        self._downloader = DownloaderRSMP()
        self._parser = ParserLicenses
        super().__init__(cpu_count=cpu_count,
                         semaphore_count=semaphore_count)

class UpdaterSNOUL(BaseFNSDataUpdater):
    """
    Дочерний класс Base_FNS_data_updater.
        Изменены параметры парсера и скачивающего класса, логика работы та же.
    """
    def __init__(self,
                 cpu_count: int = 1,
                 semaphore_count: int = 2,):
        self._downloader = DownloaderSNRUL()
        self._parser = ParserSNOUL
        super().__init__(cpu_count=cpu_count,
                         semaphore_count=semaphore_count)



class UpdaterSNOIP(BaseFNSDataUpdater):
    """
    Дочерний класс Base_FNS_data_updater.
        Изменены параметры парсера и скачивающего класса, логика работы та же.
    """
    def __init__(self,
                 cpu_count: int = 1,
                 semaphore_count: int = 2, ):
        self._downloader = DownloaderSNRIP()
        self._parser = ParserSNOIP
        super().__init__(cpu_count=cpu_count,
                         semaphore_count=semaphore_count)


if __name__ == "__main__":

    # for i in range(2):
    engine = get_sync_engine_super_user()
    sessionmaker = get_sessionmaker(sync_engine=engine)
    drop_tables_from_models(sessionmaker)
    create_tables_from_models(sessionmaker)

    st = time.perf_counter()
    #
    updater = UpdaterMainInfo(**fns_settings.model_dump())
    # file_dir = updater.download()
    file_dir = r'E:\PycharmProjects\Fns_data\tests\downloaded_dir\data-10092026-structure-12052026.zip'
    if file_dir is not None:
        updater.update_data(file_dir=file_dir, delete_file_after_update=False, rewrite_table=True, reset_table=True)

    updater = UpdaterAdditionalOkveds(**fns_settings.model_dump())
    if file_dir is not None:
        updater.update_data(file_dir=file_dir, delete_file_after_update=False, rewrite_table=True, reset_table=True)

    updater = UpdaterLicenses(**fns_settings.model_dump())
    if file_dir is not None:
        updater.update_data(file_dir=file_dir, delete_file_after_update=False, rewrite_table=True, reset_table=True)

    updater = UpdaterSNOUL(**fns_settings.model_dump())
#         file_dir = updater.download()
    file_dir = r'E:\PycharmProjects\Fns_data\tests\downloaded_dir\data-20260925-structure-20230425.zip'
    if file_dir is not None:
        updater.update_data(file_dir=file_dir, delete_file_after_update=False, rewrite_table=False, reset_table=True)

    updater = UpdaterSNOIP(**fns_settings.model_dump())
#         file_dir = updater.download()
    file_dir = r'E:\PycharmProjects\Fns_data\tests\downloaded_dir\data-20260925-structure-20241025.zip'
    if file_dir is not None:
        updater.update_data(file_dir=file_dir, delete_file_after_update=False, rewrite_table=True, reset_table=False)

    print('\n---\n', time.perf_counter() - st, ' seconds passed.')
    ...
