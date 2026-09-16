import asyncio
import multiprocessing as mp
import warnings
from abc import ABC

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from typing import Any, Final, Generator
from pathlib import Path

from zipfile import ZipFile
import time

from database_modules.core import insert_data_async
from database_modules.orm import drop_all_tables_using_models, create_all_tables_from_models
from database_modules.database_conf import settings_super_user

from src.fns_modules.fns_downloaders import Downloader
from src.fns_modules.fns_parsers import Parser_Base, Parser_SNO_UL, Parser_SNO_IP, Parser_RSMP_MAIN_INFO, Parser_RSMP_ADDITIONAL_OKVEDS
from src.fns_modules.fns_downloaders import Downloader_RSMP, Downloader_SNR




# class Base_FNS:
#     _current_xml_files = tuple()
#     _parser: Base_Parser_async = Base_Parser_async()
#     _timing: str = ''
#
#
#     @staticmethod
#     def _error_traceback(func: Callable, ):
#         @wraps(func)
#         def wrapper(self, *args, **kwargs, ):
#             try:
#                 func(self, *args, **kwargs)
#             except BaseException as e:
#                 print(e)
#                 self._clear_files()
#                 raise
#
#         return wrapper
#
#
#     def __init__(self,
#                  zipfile_dir: str, ):
#         self._zipfile_dir = zipfile_dir
#
#
#     async def _parse_and_insert_data(self,
#                                      xml_file: str,
#                                      connection_tool, ) -> None:
#         try:
#             data = await self._parser.parse_by_path(full_file_dir=f'{current_dir}/{xml_file}')
#
#             for table_name in data.keys():
#                 # # # orm
#                 # await self.engine_handler.insert_data(table_name=table_name, values=data[table_name])
#                 # # core
#                 await insert_data_async(tablename=table_name, values=data[table_name], engine=connection_tool)
#         except Exception as e:
#             print(f'{xml_file} --- {e.__class__}')
#         finally:
#             try:
#                 os.remove(fr'{current_dir}/{xml_file}')
#             except:
#                 ...
#
#     async def _get_data_async(self,
#                               l: int | None = None,
#                               limit: int | None = None, ) -> None:
#         async_engine = create_async_engine(url=settings_super_user.DATABASE_URL_ASYNC, echo=False)
#         # async_session = async_sessionmaker(async_engine)
#
#         st = time.perf_counter()
#         if not l: l = 0
#         step = 2
#         r = l + step
#         with ZipFile(self._zipfile_dir) as zf:
#             if not limit:
#                 xml_quantity = len(zf.namelist())
#             else:
#                 xml_quantity = limit
#             while True:
#                 if r > xml_quantity: r = xml_quantity
#                 self._timing = f'{r}/{xml_quantity} | {time.perf_counter() - st:.2f} seconds passed\n'
#                 print(f'\r{self._timing}', end='', flush=True)
#                 if (time.perf_counter() - st) > 60:
#                     return
#                 async with asyncio.TaskGroup() as tg:
#                     self._current_xml_files = tuple(zf.namelist()[l:r])
#                     for xml_file in self._current_xml_files:
#                         zf.extract(xml_file, path=current_dir)
#                         tg.create_task(self._parse_and_insert_data(xml_file, async_engine))
#                 if r == xml_quantity:
#                     break
#                 r += step
#                 l += step
#
#
#     def _clear_files(self, ):
#         """
#         Удаляет обрабатываемый файл при выключении программы.
#         :return:
#         """
#         for xml_file in self._current_xml_files:
#             if xml_file in os.listdir(): os.remove(f'{current_dir}/{xml_file}')
#
#
#     @_error_traceback
#     def run(self, *args, **kwargs):
#         asyncio.run(self._get_data_async(*args, **kwargs))
#         ...
#
#
# class FNS_RSMP(Base_FNS):
#     _parser = Parser_RSMP_async()
#
# class FNS_SNR(Base_FNS):
#     _parser = Parser_SNR_async()
#
# class FNS_SNRIP(Base_FNS):
#     _parser = Parser_SNRIP_async()
#
#
#
# def create_processes(xml_files_quantity: int,
#                      zipfile_dir: str,
#                      fns: type[Base_FNS],
#                      processes_quantity: int = 2, ):
#     if 0 < processes_quantity < mp.cpu_count():
#         processes = []
#         for i in range(processes_quantity):
#             l = int(xml_files_quantity / processes_quantity) * i
#             limit = int(xml_files_quantity / processes_quantity) * (i + 1)
#             if limit > xml_files_quantity: limit = xml_files_quantity
#             new_fns = fns(zipfile_dir)
#             processes.append(mp.Process(target=new_fns.run, args=(l, limit,)))
#
#         for process in processes:
#             process.start()
#         for process in processes:
#             process.join()
#         return
#
#     raise ValueError(f'Argument "processes_quantity" must be greater than 0 '
#                      f'AND lower than this machines CPU count ({mp.cpu_count()}).')



#################


async def async_generator_wrapper(sync_generator: Generator, ):
    """
    Преобразует синхронный генератор в асинхронный
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

    if parsed_data is None:
        return

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
                       data: dict[str, str | list[Any]],
                       semaphore: asyncio.Semaphore) -> None:
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
    _downloader: Downloader

    # Класс для парсинга данных, экземпляры создаются отдельно для каждого процесса.
    #   Не задается и не изменяется после инициилизации.
    _parser: type[Parser_Base]

    # Если True - zip-архив или xml-файл удаляется после всех этапов.
    #   Задается во время инициилизации.
    delete_file_after_update: bool = True

    # Количество процессов для парсинга и занесения в БД.
    #   Задается во время инициилизации.
    _cpu_count: int

    # Количество создаваемых корутин внутри отдельных процессов.
    #   Задается во время инициилизации.
    _semaphore_count: int


    def __init__(self,
                 cpu_count: int = 1,
                 semaphore_count: int = 2,
                 delete_file_after_update: bool = True, ):
        """
        Инициализация экземпляра, проверка на допустимость количества процессов.

            cpu_count принимает базовое значение, если заданный cpu_count больше макс. кол-ва логических процессоров
            или меньше или равен 0.

        :param semaphore_count:             Optional.Принимает int.
                                                Ограничение количества создаваемых корутин.

        :param cpu_count:                   Optional. принимает int.
                                                Количество создаваемых процессов.
                                                Не позволит создать больше, чем есть на машине.

        :param delete_file_after_update:    Optional. Принимает bool.
                                                Если True, то zip-архив удалится после скачивания.
        """
        print(f'{self.__class__.__name__} is updating data')
        self.delete_file_after_update = delete_file_after_update
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
                    file_dir: Path | str = None,) -> None:
        """
        Запуск апдейта данных.

            Если передается downloaded_file_dir, то скачивания нового файла не будет.

        :param file_dir:         Optional. pathlib.Path | str.
                                                Полный путь к zip-архиву.
                                                Если str, то потом конвертирует в Path.

        :return:
        """
        if isinstance(file_dir, str):
            file_dir = Path(file_dir)
        elif file_dir is None:
            print(f'{self.__class__.__name__} is downloading zip-file')
            file_dir = self._download()
        # Если ошибка во время скачивания, то вернет None.
        if file_dir is None:
            return

        xml_files_num = _xml_files_num(zip_file_dir=file_dir)
        self._create_processes(xml_files_num=xml_files_num,
                               downloaded_file_dir=file_dir, )
        if self.delete_file_after_update: Path(fr'{file_dir}').unlink(missing_ok=True)
        return
        ...


    def _download(self, ) -> Path | None:
        """
        Скачивание самого актуального zip-архива.
            Возвращает None, если не получилось скачать.
        :return:
        """
        print('"downloaded_file_dir" argument was not given. Downloading zip-archive now...\n')
        downloaded_file_dir = self._downloader.download()
        return downloaded_file_dir


    def _create_processes(self,
                          xml_files_num: int,
                          downloaded_file_dir: Path, ):
        """
        Запуск нескольких процессов для парсинга и занесения данныхв БД.

            Данные распределяются +- равномерно по процессам.
        :param xml_files_num:
        :param downloaded_file_dir:
        :return:
        """
        processes = []
        for i in range(self._cpu_count):
            left = int(xml_files_num / self._cpu_count) * i
            right = int(xml_files_num / self._cpu_count) * (i + 1) if i != self._cpu_count - 1 else xml_files_num
            if right > xml_files_num: right = xml_files_num
            processes.append(mp.Process(
                target=_run_parse_and_insert,
                args=(self._parser, downloaded_file_dir,left, right, self._semaphore_count)
            ))

        for process in processes:
            process.start()

        for process in processes:
            process.join()
        ...


def _xml_files_num(zip_file_dir: Path, ) -> int:
    """
    Возвращает количество файлов в zip-архиве.
    :param zip_file_dir:
    :return:
    """
    with ZipFile(zip_file_dir) as zf:
        xml_files_num = len(zf.namelist())
    return xml_files_num
    ...


class FNS_data_updater_RSMP_MAIN_INFO(Base_FNS_data_updater):
    """
    Дочерний класс Base_FNS_data_updater.
        Изменены параметры парсера и скачивающего класса, логика работы та же.
    """
    def __init__(self,
                 cpu_count: int = 1,
                 semaphore_count: int = 2,
                 delete_file_after_update: bool = True, ):
        self._downloader = Downloader_RSMP()
        self._parser = Parser_RSMP_MAIN_INFO
        super().__init__(cpu_count=cpu_count,
                         semaphore_count=semaphore_count,
                         delete_file_after_update=delete_file_after_update)



class FNS_data_updater_RSMP_ADDITIONAL_OKVEDS(Base_FNS_data_updater):
    """
    Дочерний класс Base_FNS_data_updater.
        Изменены параметры парсера и скачивающего класса, логика работы та же.
    """
    def __init__(self,
                 cpu_count: int = 1,
                 semaphore_count: int = 2,
                 delete_file_after_update: bool = True, ):
        self._downloader = Downloader_RSMP()
        self._parser = Parser_RSMP_ADDITIONAL_OKVEDS
        super().__init__(cpu_count=cpu_count,
                         semaphore_count=semaphore_count,
                         delete_file_after_update=delete_file_after_update)



class FNS_data_updater_SNO(Base_FNS_data_updater):
    """
    Дочерний класс Base_FNS_data_updater.
        Изменены параметры парсера и скачивающего класса, логика работы та же.
    """
    def __init__(self,
                 cpu_count: int = 1,
                 semaphore_count: int = 2,
                 delete_file_after_update: bool = True, ):
        self._downloader = Downloader_SNR()
        self._parser = Parser_SNO_UL
        super().__init__(cpu_count=cpu_count,
                         semaphore_count=semaphore_count,
                         delete_file_after_update=delete_file_after_update)



class FNS_data_updater_SNO_IP(Base_FNS_data_updater):
    """
    Дочерний класс Base_FNS_data_updater.
        Изменены параметры парсера и скачивающего класса, логика работы та же.
    """
    def __init__(self,
                 cpu_count: int = 1,
                 semaphore_count: int = 2,
                 delete_file_after_update: bool = True, ):
        self._downloader = Downloader_SNR()
        self._parser = Parser_SNO_IP
        super().__init__(cpu_count=cpu_count,
                         semaphore_count=semaphore_count,
                         delete_file_after_update=delete_file_after_update)





# def fns_old():
#     drop_all_tables_using_models()      # Придумать чо-нить, тк вечно удалять и создавать таблицы - гавно идея.
#     create_all_tables_from_models()     # Продолжение.
#
#     # # Разкоментить для нормальных тестов
#     # downloaded_files_dirs = {'rsmp': Downloader_RSMP()(),
#     #                          'snr': Downloader_SNR()(),
#     #                          'snrip': Downloader_SNRIP()(), }
#
#     downloaded_files_dirs_placeholder = {'rsmp': f'{current_dir}/downloaded_dir/data-10072026-structure-12052026.zip',
#                                          'snr': f'{current_dir}/downloaded_dir/data-20260625-structure-20230425.zip',
#                                          'snrip': f'{current_dir}/downloaded_dir/data-20260625-structure-20241025.zip', }
#
#     for key in downloaded_files_dirs_placeholder.keys():
#         with ZipFile(downloaded_files_dirs_placeholder[key]) as zf:
#             xml_files_quantity = len(zf.namelist())
#         if key == 'rsmp': create_processes(xml_files_quantity=xml_files_quantity,
#                                            processes_quantity=4,
#                                            zipfile_dir=downloaded_files_dirs_placeholder[key],
#                                            fns=FNS_RSMP, )
#
#         elif key == 'snr': create_processes(xml_files_quantity=xml_files_quantity,
#                                             processes_quantity=4,
#                                             zipfile_dir=downloaded_files_dirs_placeholder[key],
#                                             fns=FNS_SNR, )
#
#         elif key == 'snrip':create_processes(xml_files_quantity=xml_files_quantity,
#                                              processes_quantity=4,
#                                              zipfile_dir=downloaded_files_dirs_placeholder[key],
#                                              fns=FNS_SNRIP, )
#         else:
#             ...




def fns_new():
    drop_all_tables_using_models()
    create_all_tables_from_models()

    st = time.perf_counter()
    FNS_data_updater_RSMP_MAIN_INFO(cpu_count=8,
                                    semaphore_count=10,
                                    delete_file_after_update=False).update_data(
        file_dir=r'E:\PycharmProjects\MegaParsers\src\downloaded_dir\data-10082026-structure-12052026.zip')
    FNS_data_updater_RSMP_ADDITIONAL_OKVEDS(cpu_count=8,
                                            semaphore_count=10,
                                            delete_file_after_update=False).update_data(
        file_dir=r'E:\PycharmProjects\MegaParsers\src\downloaded_dir\data-10082026-structure-12052026.zip',)
    FNS_data_updater_SNO(cpu_count=8,
                         semaphore_count=10,
                         delete_file_after_update=False).update_data(
        file_dir=r'E:\PycharmProjects\MegaParsers\src\downloaded_dir\data-20260625-structure-20230425.zip')
    FNS_data_updater_SNO_IP(cpu_count=8,
                            semaphore_count=10,
                            delete_file_after_update=False).update_data(
        file_dir=r'E:\PycharmProjects\MegaParsers\src\downloaded_dir\data-20260625-structure-20241025.zip')
    print('\n---\n', time.perf_counter() - st, ' seconds passed.')


if __name__ == '__main__':
    fns_new()
    ...
