from src.relevant_okveds_modules import *
from typing import Any
from sqlalchemy.engine import create_engine

from src.database_modules.core import rename_tables, drop_temp_table
from src.database_modules.orm import drop_tables_from_models, create_tables_from_models
from src.database_modules.database_conf import settings_super_user
from src.database_modules.core import insert_data



class Relevant_okveds_updater:
    """
    Пример использования:
        updater = Relevant_okveds_updater()
        data = updater.download()
        updater.update_data(xlsx_file_data=data, rewrite_table=True)

    """
    def __init__(self, ):
        self._downloader = Downloader_relevant_okveds()
        self._parser = Parser_relevant_okveds()

    def download(self, ) -> str:
        """
        Скачивание xlsx-файла.
            Возвращает полученные данные, декодированные utf-8, в формате str.
        :return:
        """
        return self._downloader.download()

    def update_data(self,
                    xlsx_file_data: str,
                    rewrite_table: bool = False, ):
        """
            Парсит данные и заносит их в таблицу.

        :param xlsx_file_data:      str. Данные из xlsx-файла.
        :param rewrite_table:       bool. Если True, то перезапишет данные из shadow_table в основную,
                                        удалив shadow_table.
        :return:
        """
        if not xlsx_file_data:
            return
        self._initialize_table()

        data = self._parse(xlsx_file_data=xlsx_file_data)

        self._insert_data(data=data)

        if rewrite_table:
            self._replace_tables()
            self._drop_temp_table()


    def _insert_data(self,
                     data: dict[str, str | None | list[Any]], ):
        """
        Запись данных в shadow_table.
        :param data: 
        :return:
        """
        engine = create_engine(url=settings_super_user.DATABASE_URL)
        tablename = data['tablename']
        insert_data(tablename=tablename, values=data['data'], engine=engine)


    def _initialize_table(self, ):
        drop_tables_from_models(tables_models=[self._parser._database_model])
        create_tables_from_models(tables_models=[self._parser._database_model,
                                                 self._parser._database_model.__nonshadow_table__])


    def _parse(self, xlsx_file_data: str, ) -> dict[str, str | None | list[Any]]:
        return self._parser.parse(xlsx_file_data=xlsx_file_data)


    def _replace_tables(self, ):
        rename_tables(new_tablename=self._parser._database_model.__tablename__,
                      old_tablename=self._parser._database_model.__nonshadow_table__.__tablename__)

    def _drop_temp_table(self, ):
        drop_temp_table(tablename=self._parser._database_model.__nonshadow_table__.__tablename__)



