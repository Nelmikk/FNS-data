from src.database_modules.database_sessions import batch_data, async_engine, sync_engine
from src.models.database_models import models_dict

from sqlalchemy import insert, MetaData, inspect, text
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.engine.base import Engine



@batch_data(batch_size=16_000)
async def insert_data_async(tablename: str,
                            values: list[dict],
                            engine: AsyncEngine = None, ):
    if not engine:
        engine = async_engine

    async with engine.connect() as connection:
        query = insert(models_dict[tablename].__table__)
        await connection.execute(query, values)
        await connection.commit()
    ...


def drop_all_tables_using_metadata(connection_tool: Engine | None, ):
    """
    Дропает все таблицы, которые есть в схеме.
    :return:
    """
    engine = connection_tool if connection_tool else sync_engine
    metadata = MetaData()
    metadata.reflect(bind=engine)
    metadata.drop_all(bind=engine)
    ...


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