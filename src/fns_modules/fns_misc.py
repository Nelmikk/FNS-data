from functools import wraps
from pathlib import Path
from typing import Generator
from zipfile import ZipFile
from lxml import etree
import logging


class Unzipper:
    def unzip_data(self,
                   file_dir: str | Path,
                   left: int = 0,
                   right: int = 0, ):
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
                logging.error('Error reading zip-file. Zip-file could be corrupted.')
                yield None
        else:
            yield etree.parse(file_dir).getroot()



class File_reader:
    def get_file_root(self,
                      file_dir: str | Path, ) -> etree._Element:
        """
        Возвращает объект типа _Element для парсинга.
        :param file_dir:
        :return:
        """
        root = etree.parse(file_dir).getroot()
        return root


def retry(retry_nums: int = 1, ):
    def f(func, ):
        @wraps(func)
        def wrapper(*args, **kwargs, ):
            retry_num = 0
            while True:
                retry_num += 1

                if retry_num > retry_nums:
                    return False
                print(f'\n{retry_num} attempt ...')
                logging.info(f'{retry_num} attempt ...')
                if func(*args, **kwargs) is True:
                    return True
        return wrapper
    return f