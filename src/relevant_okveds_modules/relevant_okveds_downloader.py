import requests


class Downloader_relevant_okveds:
    def __init__(self, ):
        ...

    def download(self, ) -> str:
        xlsx_file_data = ''
        try:
            xlsx_file_data = (requests.get('https://classifikators.ru/assets/downloads/okved/okved.csv').
                              content.decode('utf-8'))
        finally:
            return xlsx_file_data


Downloader_relevant_okveds().download()