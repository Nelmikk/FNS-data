from pathlib import Path
from typing import Generator
from zipfile import ZipFile
from lxml import etree



class Unzipper:
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
    def get_file_root(self,
                      file_dir: str | Path, ) -> etree._Element:
        root = etree.parse(file_dir).getroot()
        return root