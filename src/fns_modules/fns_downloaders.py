import requests
from pathlib import Path
from bs4 import BeautifulSoup
import re
import logging

from src.errors.downloader_errors import CanNotCreateDirectory


class DownloaderBase:
    download_dir: Path = Path(fr'{Path.cwd()}/downloaded_dir')
    _page_url = None
    attempts = 5

    _filename = 'downloaded_file.zip'
    def __init__(self, log_filename: str = 'fns_log.log', ):
        logging.basicConfig(level=logging.INFO, filename=log_filename,
                            filemode='w', format='%(asctime)s %(levelname)s %(message)s')

    @property
    def _file_url(self, ) -> str:
        """
        Собирает необходимую инфу для скачивания.
        Находит ЮРЛ файла и задает для него имя.
        :return:
        """
        page_content = requests.get(self._page_url, stream=True).content
        page_content = BeautifulSoup(page_content, 'lxml')
        file_url = [i for i in page_content.find_all(string=re.compile('opendata')) if '.zip' in i][0]
        self._filename = file_url.split(sep='/')[-1]

        return file_url


    def _del_error_file(self, ):
        """
        Удаляет частчно скачанный файл.
        :return:
        """
        try:
            Path.unlink(Path(fr'{self.download_dir}/{self._filename}'))
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



    def _check_filename(self, ):
        """
        Проверяет, чтобы новый скачанный файл не перезаписывал предыдущий - меняет имя нового файла.
        :return:
        """
        while True:
            i = 1
            if not (self._filename in Path.iterdir(self.download_dir)):
                break
            logging.warning(f'{self._filename} is already in download directory. '
                            f'The file will be named {i}_{self._filename}. - {self.__class__.__name__}')
            self._filename = f'{i}_{self._filename}'
            i += 1


    def _download(self, ) -> bool:
        """
        Скачивание zip-архива.
            Если скачивание прерывается, то пробует скачать с того же места,
            если не получается, то пробует скачать по новой.
        """
        file_url = self._file_url
        downloaded_bytes = 0

        for attempt in range(self.attempts):
            headers = {'Range': f'bytes={downloaded_bytes}-', }
            try:
                with requests.get(url=file_url, headers=headers, stream=True, timeout=30) as response:
                    if response.status_code == 200:
                        mode = 'wb'
                        downloaded_bytes = 0
                    elif response.status_code == 206:
                        mode = 'ab' if downloaded_bytes > 0 else 'wb'
                    else:
                        print(f'Request got status code {response.status_code} - {self.__class__.__name__}')
                        logging.warning(f'Request got status code {response.status_code} - {self.__class__.__name__}')
                        return False

                    with open(f'{self.download_dir}/{self._filename}', mode) as f:
                        for chunk in response.iter_content(chunk_size=1024 * 1024):
                            f.write(chunk)
                            downloaded_bytes += 1024 * 1024
                            print(f'\r{self._filename} downloading... {downloaded_bytes} bytes. '
                                  f'--- {self.__class__.__name__}',
                                  end='',
                                  flush=True)
                    return True
            except:
                print('\nError while downloading file...')
        print(f'File was not downloaded - {self.__class__.__name__}')
        logging.error(f'File was not downloaded - {self.__class__.__name__}')
        self._del_error_file()
        return False




    def download(self, ) -> Path | None:
        """
        Вовзращает название записанного файла при успехе, иначе - None.
        :return:
        """
        if self._page_url is None:
            logging.critical(f'Page content was changed, downloader must be updated. --- {self.__class__.__name__}')
            return None
        if not self._check_download_dir():
            return None
        if not self._download():
            return None
        return Path(f'{self.download_dir}/{self._filename}')



class DownloaderRSMP(DownloaderBase):
    def __init__(self, ):
        self._page_url = 'https://www.nalog.gov.ru/opendata/7707329152-rsmp/'
        super().__init__()

class DownloaderSNRUL(DownloaderBase):
    def __init__(self, ):
        self._page_url = 'https://www.nalog.gov.ru/opendata/7707329152-snr/'
        super().__init__()

class DownloaderSNRIP(DownloaderBase):
    def __init__(self, ):
        self._page_url = 'https://www.nalog.gov.ru/opendata/7707329152-snrip/'
        super().__init__()

__all__ = ['DownloaderRSMP',
           'DownloaderSNRIP',
           'DownloaderSNRUL',
           'DownloaderBase', ]