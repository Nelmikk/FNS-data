from src.database_modules.database_sessions import async_engine, sync_engine
from src.database_modules.database_misc import batch_data
from src.models.database_models import models_dict, Base

from sqlalchemy import insert, inspect, text
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.engine.base import Engine



@batch_data(batch_size=16_000)
async def insert_data_async(tablename: str,
                            values: list[dict],
                            engine: AsyncEngine = async_engine, ):
    async with engine.connect() as connection:
        query = insert(models_dict[tablename].__table__)
        await connection.execute(query, values)
        await connection.commit()
    ...

@batch_data(batch_size=16_000)
def insert_data(tablename: str,
                values: list[dict],
                engine: Engine = sync_engine, ):
    with engine.connect() as connection:
        query = insert(models_dict[tablename].__table__)
        connection.execute(query, values)
        connection.commit()
    ...

# async def rename_tables_async(engine: AsyncEngine | None,
#                               *args, ):
#     """
#     Обновляет название таблиц в одной транзакции.
#
#     :param engine:
#     :param args:        tuple(old_tablename: str, new_tablename: str).
#     :return:
#     """
#     engine = engine if engine else async_engine
#     async with engine.connect() as connection:
#         for old_name, new_name in args:
#             if old_name not in [i.__tablename__ for i in Base.__subclasses__()]:
#                 continue
#
#             query = text(f"ALTER TABLE {old_name} RENAME TO {new_name};")
#             await connection.execute(query)
#         await connection.commit()


async def replace_tables_async(old_table_name: str,
                               new_table_name: str,
                               engine: AsyncEngine = async_engine, ):
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
    query = text(f'ALTER INDEX IF EXISTS {old_index_name} RENAME TO {new_index_name};')

    with engine.connect() as connection:
        connection.execute(query)
        connection.commit()

# def drop_all_tables_using_metadata(engine: Engine = sync_engine, ):
#     """
#     Дропает все таблицы, которые есть в схеме.
#     :return:
#     """
#     # metadata = MetaData()
#     # metadata.reflect(bind=engine)
#     # metadata.drop_all(bind=engine)
#     database_models.Base.metadata.drop_all(bind=engine,
#                                            tables=[i.__table__ for i in database_models.Base.__subclasses__()])



# def reset_tables(engine: Engine = sync_engine,
#                  tables=list[type[database_models.Base]], ):
#     database_models.Base.metadata.drop_all()



async def switch_schema(engine: AsyncEngine,
                        schema_name: str, ):
    """
    Меняет рабочую схему.
    :param engine:
    :param schema_name:
    :return:
    """
    if schema_name in inspect(engine).get_schema_names():
        async with engine.connect() as connection:
            await connection.execute(text(f'SET search_path TO {schema_name};'))
    else:
        raise ValueError(f'No schema named "{schema_name}" in database.')