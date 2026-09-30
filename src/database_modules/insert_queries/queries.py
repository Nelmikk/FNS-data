from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.engine.base import Engine
from sqlalchemy import insert

from src.database_modules.database_sessions import async_engine, sync_engine
from src.database_modules.insert_queries.misc import batch_data
from src.models.database_models import models_dict


@batch_data(batch_size=14_000)
async def insert_data_async(tablename: str,
                            values: list[dict],
                            engine: AsyncEngine = async_engine, ) -> None:
    """
    Асинхронное внесение данных в БД.
    :param tablename:
    :param values:
    :param engine:
    :return:
    """
    async with engine.connect() as connection:
        query = insert(models_dict[tablename].__table__)
        await connection.execute(query, values)
        await connection.commit()

@batch_data(batch_size=14_000)
def insert_data(tablename: str,
                values: list[dict],
                engine: Engine = sync_engine, ) -> None:
    """
    Синхронное внесение данных в БД.
    :param tablename:
    :param values:
    :param engine:
    :return:
    """
    with engine.connect() as connection:
        query = insert(models_dict[tablename].__table__)
        connection.execute(query, values)
        connection.commit()