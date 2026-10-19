from pathlib import Path
from typing import Generator
from zipfile import ZipFile
from lxml import etree
import logging
import json


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


def check_latest_files(updater_classname: str,
                       filename: str, ) -> bool:
    """
    Проверяет последний скачанный файл по названию класса апдейтера.
        Возвращает True, если данные из файла уже в БД, иначе - False.
    """
    if not Path.cwd().joinpath(Path('latest_files/latest_files.json')).exists():
        Path.cwd().joinpath(Path('latest_files')).mkdir(exist_ok=True)
        return False

    with open(Path.cwd().joinpath(Path('latest_files/latest_files.json')), 'r') as f:
        latest_files = dict(json.loads(f.read()))
        if updater_classname not in latest_files.keys():
            return False

        if latest_files[updater_classname] != filename:
            return False
    return True


def update_latest_files(updater_classname: str,
                        filename: str, ):
    """
    Обновляет json-файл с последними файлами, данные с которых добавились в БД.
    """
    latest_files = dict()
    if Path.cwd().joinpath(Path('latest_files/latest_files.json')).exists():
        with open(Path.cwd().joinpath(Path('latest_files/latest_files.json')), 'r') as f:
            latest_files = dict(json.loads(f.read()))
    latest_files[updater_classname] = filename

    with open(Path.cwd().joinpath(Path('latest_files/latest_files.json')), 'w') as f:
        f.write(json.dumps(latest_files, ensure_ascii=False))
