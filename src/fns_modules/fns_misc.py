from pathlib import Path
from typing import Generator, Callable
from functools import wraps
from zipfile import ZipFile
from lxml import etree

from src.fns_modules.fns_errors import DirectoryDoesNotExist, WrongFileExtension



# def check_file(expected_extension: str | list[str], ) -> Callable:
#     """
#     Проверка файла и пути к файлу.
#     :param expected_extension:
#     :return:
#     """
#     expected_extension = [expected_extension] if isinstance(expected_extension, str) else expected_extension
#     def checker(func: Callable, ):
#         @wraps(func)
#         def wrapper(
#                 *args, **kwargs, ):
#             file_dir = kwargs['file_dir'] if 'file_dir' in kwargs else args[1]
#             nonlocal expected_extension
#             if expected_extension:
#                 # if not str(file_dir).endswith(expected_extension): raise WrongFileExtension(file_dir, expected_extension)
#                 if not any([str(file_dir).endswith(i) for i in expected_extension]): raise WrongFileExtension
#             if not Path(file_dir).exists(): raise DirectoryDoesNotExist(file_dir)
#             return func(*args, **kwargs)
#
#         return wrapper
#     return checker




class Unzipper:
    # @check_file(expected_extension='.zip')
    def unzip_file(self,
                   file_dir: str | Path,
                   unzip_dir: str | Path | None = Path.cwd(),
                   left: int = 0,
                   right: int = 0, ) -> Generator:
        unzip_dir = unzip_dir if unzip_dir else Path.cwd()

        with ZipFile(file_dir, 'r') as zf:
            if right is None:
                right = len(zf.namelist())
            left = left if left >= 0 else 0

            right = right if right <= len(zf.namelist()) else len(zf.namelist())

            files = zf.namelist()[left:right]

            for file in files:
                zf.extract(member=file, path=unzip_dir)
                yield Path(f'{unzip_dir}/{file}')


    # @check_file(expected_extension=['.zip', '.xml'])
    def unzip_data(self,
                   file_dir: str | Path,
                   left: int = 0,
                   right: int = 0, ):
        """
        Генератор данных из файлов, находящихся в zip-архиве.
        :param file_dir:
        :param left:
        :param right:
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
    # @check_file(expected_extension='.xml')
    def get_file_root(self,
                      file_dir: str | Path, ) -> etree._Element:
        root = etree.parse(file_dir).getroot()
        return root
        ...