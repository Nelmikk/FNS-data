import requests
from pathlib import Path
from bs4 import BeautifulSoup
import re
import logging

from src.errors.downloader_errors import DownloadError, CanNotCreateDirectory
from src.fns_modules.fns_misc import retry


class Downloader_Base:
    download_dir: Path = Path(fr'{Path.cwd()}\downloaded_dir')
    _page_url = None

    _file_name = 'downloaded_file.zip'
    def __init__(self, log_filename: str = 'fns_log.log', ):
        logging.basicConfig(level=logging.INFO, filename=log_filename, filemode='w')



    def _del_error_file(self, ):
        """
        Удаляет частчно скачанный файл.
        :return:
        """
        try:
            Path.unlink(Path(fr'{self.download_dir}\{self._file_name}'))
            logging.info(f'Partially downloaded file is deleted. - {self.__class__.__name__}')
        except:
            logging.warning(f'Partially downloaded file is not deleted. - {self.__class__.__name__}')


    def _check_download_dir(self, ):
        """
        Проверяет, существует ли директория для скачивания.
        :return:
        """
        try:
            if not self.download_dir.exists():
                self.download_dir.mkdir()
            return True
        except CanNotCreateDirectory as e:
            logging.error(f'Can not create directory {self.download_dir}. - {self.__class__.__name__}', exc_info=True)
            return False



    def _check_file_name(self, ):
        """
        Проверяет, чтобы новый скачанный файл не перезаписывал предыдущий - меняет имя нового файла.
        :return:
        """
        while True:
            i = 1
            if not (self._file_name in Path.iterdir(self.download_dir)):
                break
            logging.warning(f'{self._file_name} is already in download directory. '
                            f'The file will be named {i}_{self._file_name}. - {self.__class__.__name__}')
            self._file_name = f'{i}_{self._file_name}'
            i += 1


    def _write_response(self,
                        response: requests.models.Response, ) -> bool:
        """
        :param response:
        :return:
        """
        self._check_file_name()

        downloaded = 0
        try:
            with open(fr'{self.download_dir}\{self._file_name}', 'wb') as f:
                for content in response.iter_content(chunk_size=1_000_000):
                    f.write(content)
                    downloaded += 1_000_000
                    print(f'\r{self._file_name} downloading... {downloaded} bytes. '
                          f'--- {self.__class__.__name__}',
                          end='',
                          flush=True)
                logging.info(f'File downloaded - {self.__class__.__name__}')
                return True
        except Exception as e:
            self._del_error_file()
            logging.error(f'Error while downloading file {self._file_name}. - {self.__class__.__name__}', exc_info=True)
            return False



    @property
    def _file_url(self, ) -> str:
        """
        Собирает необходимую инфу для скачивания.
        Находит ЮРЛ файла и задает для него имя.
        :return:
        """
        page_content = requests.get(self._page_url, stream=True).content
        page_content = BeautifulSoup(page_content, 'lxml')
        file_url = [i for i in page_content.find_all(string=re.compile('https://file.nalog.ru/opendata'))
                          if '.zip' in i][0]
        self._file_name = file_url.split(sep='/')[-1]

        return file_url

    @retry(retry_nums=3)
    def _download(self, ) -> bool:
        file_url = self._file_url
        response = requests.get(url=file_url, stream=True)
        if response.status_code == 200:
            if self._write_response(response=response):

                return True

            return False

        logging.warning(f'File Status code - {response.status_code} - {self.__class__.__name__}')
        return False


    def download(self, ) -> Path | None:
        """
        Вовзращает название записанного файла при успехе, иначе - None.
        :return:
        """
        if self._page_url is None:
            logging.critical('Page content was changed, downloader must be updated.  - {self.__class__.__name__}')
            return None
        if not self._check_download_dir():
            return None
        if not self._download():
            return None
        return Path(f'{self.download_dir}/{self._file_name}')



class Downloader_RSMP(Downloader_Base):
    def __init__(self, ):
        self._page_url = 'https://www.nalog.gov.ru/opendata/7707329152-rsmp/'
        super().__init__()

class Downloader_SNR(Downloader_Base):
    def __init__(self, ):
        self._page_url = 'https://www.nalog.gov.ru/opendata/7707329152-snr/'
        super().__init__()

class Downloader_SNRIP(Downloader_Base):
    def __init__(self, ):
        self._page_url = 'https://www.nalog.gov.ru/opendata/7707329152-snrip/'
        super().__init__()

__all__ = ['Downloader_RSMP', 'Downloader_SNRIP', 'Downloader_SNR', 'Downloader_Base']