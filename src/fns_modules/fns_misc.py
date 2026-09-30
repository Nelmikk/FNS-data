from pathlib import Path
from typing import Generator
from zipfile import ZipFile
from lxml import etree



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
            with ZipFile(file_dir, 'r') as zf:
                if right is None:
                    right = len(zf.namelist())
                left = left if left >= 0 else 0

                right = right if 0 < right <= len(zf.namelist()) else len(zf.namelist())

                files = zf.namelist()[left:right]

                for file in files:
                    yield etree.fromstring(zf.open(file).read())
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