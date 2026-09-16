# import sqlalchemy
# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession    # Для асинхронного подключения
# from sqlalchemy import create_engine, text, insert
# from sqlalchemy.util import memoized_property
#
# from database_tables import metadata_obj
#
#
# from database_modules.database_conf import settings_super_user
#
#
#
# # async_engine = create_async_engine(
# #     url=settings_super_user.DATABASE_URL_ASYNC,
# #     echo=True,
# # )
# #
# # sync_engine = create_engine(
# #     url=settings_super_user.DATABASE_URL,
# #     echo=False
# # )
#
# tables_dict = metadata_obj.tables
#
# class Sync_engine:
#     def __init__(self,
#                  url: str | None = None,
#                  engine: sqlalchemy.engine.base.Engine|None = None, ):
#         if not not engine and not url:
#             raise ValueError('Requires two arguments, none were given')
#         if not engine:
#             self.__engine = create_engine(url)
#             # print(type(self.__engine))
#             return
#         self.__engine = engine
#         ...
#
#
#     def drop_all_tables(self, ):
#         """
#         Удаляет все таблцы, объявленные в database_tables.py.
#         :return:
#         """
#         metadata_obj.drop_all(self.__engine)
#
#
#     def create_all_tables(self, ):
#         """
#         Создает все таблицы, объявленные в database_tables.py.
#         :return:
#         """
#         metadata_obj.create_all(self.__engine)
#
#
#     def insert(self,
#                table: str,
#                values: dict | list, ):
#         """
#         Вставляет данные в выбранную таблицу.
#         :param table:
#         :param values:
#         :return:
#         """
#         if isinstance(values, dict):
#             values = [values]
#
#         with self.__engine.connect() as connection:
#             query = insert(tables_dict[table]).values(
#                 values
#             )
#             connection.execute(query)
#             connection.commit()
#         ...
#
#     def select(self, ):
#
#         ...
#
#
# sync_engine = Sync_engine(url=settings_super_user.DATABASE_URL)