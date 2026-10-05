from functools import wraps
from pathlib import Path
from typing import AsyncGenerator, Generator
from zipfile import ZipFile
from lxml import etree
import logging
from inspect import iscoroutinefunction


class Unzipper:
    def unzip_data(self,
                   file_dir: str | Path,
                   left: int = 0,
                   right: int = 0, ) -> Generator:
        """
        Генератор данных из файлов, находящихся в zip-архиве.

            Возвращает данные из заданных переменными (left, right) границ: zf.namelist()[left:right].
            Если файл в file_dir имеет расшинерие .xml, то left и right игнорируются.

        :param file_dir:    Или zip-архив, или xml-файл.
        :param left:        Левая граница при парсинге.
        :param right:       Правая граница при парсинге.
        :return:
        """
        if str(file_dir).endswith('.zip'):
            try:
                with ZipFile(file_dir, 'r') as zf:
                    if right is None:
                        right = len(zf.namelist())
                    left = left if left >= 0 else 0

                    right = right if 0 < right <= len(zf.namelist()) else len(zf.namelist())

                    files = zf.namelist()[left:right]

                    for file in files:
                        yield etree.fromstring(zf.open(file).read())
            except Exception as e:
                logging.error(f'Error reading zip-file. Zip-file could be corrupted. {file_dir}')
                yield None
        else:
            try:
                yield etree.parse(file_dir).getroot()
            except:
                logging.error(f'Error parsing xml-file. Xml-file could be corrupted. {file_dir}')
                yield None



class FileReader:
    def get_file_root(self,
                      file_dir: str | Path, ) -> etree._Element | None:
        """
        Возвращает объект типа _Element для парсинга.
        :param file_dir:
        :return:
        """
        try:
            root = etree.parse(file_dir).getroot()
            return root
        except:
            logging.error(f'Error parsing xml-file. Xml-file could be corrupted. {file_dir}')
            return None



def retry(attempts: int = 1, ):
    """
    Декоратор для повторных попыток функций/методов, которые возвращают False при неудаче.
    attempts: int - количество попыток
    """
    attempts = attempts if attempts > 0 else 1
    def f(func, ):
        @wraps(func)
        def sync_wrapper(*args, **kwargs, ):

            for attempt_num in range(attempts):

                if attempt_num > attempts:
                    return False

                print(f'\n{attempt_num} attempt ...')
                logging.info(f'{attempt_num} attempt ...')
                if func(*args, **kwargs) is True:
                    return True

        @wraps(func)
        def async_wrapper(*args, **kwargs, ):
            for attempt_num in range(attempts):

                if attempt_num > attempts:
                    return False

                print(f'\n{attempt_num} attempt ...')
                logging.info(f'{attempt_num} attempt ...')
                if func(*args, **kwargs) is True:
                    return True

        if iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return f