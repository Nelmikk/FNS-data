from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from src.models.database_models import Base
from src.database_modules.database_sessions import async_engine, sync_engine, sync_session


async def replace_tables_async(old_table_name: str,
                               new_table_name: str,
                               engine: AsyncEngine = async_engine, ):
    """
    Заменяет старую таблицу новой.
    :param old_table_name:
    :param new_table_name:
    :param engine:
    :return:
    """
    drop_query = text(f'DROP TABLE IF EXISTS {old_table_name};')
    rename_query = text(f'ALTER TABLE {new_table_name} RENAME TO {old_table_name};')
    analyze_query = text(f'ANALYZE {old_table_name};')

    async with engine.connect() as connection:
        await connection.execute(drop_query)
        await connection.execute(rename_query)
        await connection.execute(analyze_query)
        await connection.commit()


def rename_tables(old_tablename: str,
                  new_tablename: str,
                  engine: Engine = sync_engine, ):
    """
    Меняет местами названя старой и новой таблиц.
    :param old_tablename:
    :param new_tablename:
    :param engine:
    :return:
    """
    # Удаление временной таблицы, если она осталась после ошибки в предыдущих циклах обновления данных.
    drop_temp_table(tablename=old_tablename, engine=engine)
    rename_old_table_query = text(f'ALTER TABLE {old_tablename} RENAME TO TEMPORARY_TABLE_{old_tablename};')
    rename_new_table_query = text(f'ALTER TABLE {new_tablename} RENAME TO {old_tablename};')
    analyze_query = text(f'ANALYZE {old_tablename};')

    with engine.connect() as connection:
        connection.execute(rename_old_table_query)
        connection.execute(rename_new_table_query)
        connection.execute(analyze_query)
        connection.commit()


def drop_temp_table(tablename: str,
                    engine: Engine = sync_engine, ):
    """
    Удаление временной таблицы, если она осталась после ошибки в предыдущих циклах обновления данных.
    :param tablename:
    :param engine:
    :return:
    """

    with engine.connect() as connection:
        connection.execute(text(f'DROP TABLE IF EXISTS TEMPORARY_TABLE_{tablename};'))
        connection.commit()



def create_index(index_name: str,
                 column_index: str,
                 table: type[Base],
                 engine: Engine = sync_engine,
                 index_type: str = 'btree'):
    """
    Удаляет индекс, если он существует и создает его.
    :param index_name:
    :param column_index:
    :param table:
    :param engine:
    :param index_type:
    :return:
    """
    if table not in Base.__subclasses__():
        return

    drop_query = text(f'DROP INDEX IF EXISTS {index_name};')

    create_query = text(f'CREATE INDEX {index_name} ON {table.__tablename__} USING {index_type}({column_index});')
    with engine.connect() as connection:
        connection.execute(drop_query)
        connection.execute(create_query)
        connection.commit()


def rename_index(old_index_name: str,
                 new_index_name: str,
                 engine: Engine = sync_engine, ):
    """
    Изменение названия индекса.
    :param old_index_name:
    :param new_index_name:
    :param engine:
    :return:
    """
    query = text(f'ALTER INDEX IF EXISTS {old_index_name} RENAME TO {new_index_name};')

    with engine.connect() as connection:
        connection.execute(query)
        connection.commit()



def create_tables_from_models(tables_models: list[type[Base, ]] | None = None,
                             session: sessionmaker = sync_session, ):
    """
    Создание таблиц из описанных моделей.
    :param tables_models:   Если == None, то будут созданы все описанные таблицы.
    :param session:
    :return:
    """
    if tables_models is not None:
        tables_models = [table_model.__table__ for table_model in tables_models]
    with session().connection() as connection:
        Base.metadata.create_all(bind=connection, tables=tables_models)
        connection.commit()

def drop_tables_from_models(tables_models: list[type[Base, ]] | None = None,
                            session: sessionmaker = sync_session, ):
    """
    Удаление таблиц из описанных моделей.
    :param tables_models:   Если == None, то будут удалены все описанные таблицы.
    :param session:
    :return:
    """
    if tables_models is not None:
        tables_models = [table_model.__table__ for table_model in tables_models]
    with session().connection() as connection:
        Base.metadata.drop_all(bind=connection, tables=tables_models)
        connection.commit()
