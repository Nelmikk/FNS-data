import sqlalchemy
from sqlalchemy.orm import load_only
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from src.database_modules.database_sessions import async_session, sync_session, batch_data
from src.models.database_models import Base, fns_main_info, okveds, models_dict


@batch_data(16_000)
async def insert_data_async(table_name: str,
                            values: list[dict],
                            connection_tool: async_sessionmaker | None = None, ):
    """
    Асинхронное добавление в таблицу.
    :param connection_tool:
    :param table_name:
    :param values:
    :return:
    """

    upsert_query = insert(models_dict[table_name]).values(values)

    if connection_tool is None:
        # print('No session')
        async with async_session() as new_session:
            await new_session.execute(upsert_query)
            await new_session.commit()
        return

    async with connection_tool() as new_session:
        await new_session.execute(upsert_query)
        await new_session.commit()
        ...



async def select_fns_main_info_by_inn_async(inn: int, ) -> sqlalchemy.engine.result.ScalarResult:
    """
    Возвращает инфу из fns_main_info по заданному ИНН в виде генератора.
    :param inn:
    :return:
    """
    async with async_session() as session:
        statement = select(fns_main_info).where(fns_main_info.inn==inn)
        result = await session.scalars(statement)
    return result


async def select_fns_main_info_by_ogrn_async(ogrn: int, ) -> sqlalchemy.engine.result.ScalarResult:
    """
    Возвращает инфу из fns_main_info по заданному ОГРН.
    :param ogrn:
    :return:
    """
    async with async_session() as session:
        statement = select(fns_main_info).where(fns_main_info.ogrn==ogrn)
        result = await session.scalars(statement)
    return result
    ...


async def select_additional_okveds_by_inn_async(inn: int, ) -> sqlalchemy.engine.result.ScalarResult:
    """
    Возвращает доп ОКВЭДы организации по заданному ИНН.
    :param inn:
    :return:
    """
    async with async_session() as session:
        statement = select(okveds).where(okveds.inn==inn)
        result = await session.scalars(statement)
    return result
    ...

async def select_additional_okveds_by_ogrn_async(ogrn: int,
                                                 *attrs: sqlalchemy.orm.attributes.InstrumentedAttribute, ) -> sqlalchemy.engine.result.ScalarResult:
    """
    Возвращает доп ОКВЭДы организации по заданному ОГРН.
    :param ogrn:
    :return:
    """
    statement = select(okveds).where(okveds.ogrn == ogrn)
    if attrs: statement = statement.options(load_only(*attrs))

    async with async_session() as session:
        # statement = select(okveds).where(okveds.ogrn == ogrn)
        result = await session.scalars(statement)
        return result


# def drop_all_tables_using_models(session: sessionmaker = sync_session, ):
#     """
#     Дропает все таблицы, объявленные в database_models.py (которые наследуются от Base).
#     :return:
#     """
#     with session().connection() as connection:
#         Base.metadata.drop_all(bind=connection)
#         connection.commit()
#
#
# def create_all_tables_from_models(session: sessionmaker = sync_session, ):
#     """
#     Создание всех таблиц, объявленных в database_models.py (которые наследуются от Base).
#     :return:
#     """
#     with session().connection() as connection:
#         Base.metadata.create_all(bind=connection)
#         connection.commit()


def create_tables_from_models(tables_models: list[type[DeclarativeBase]],
                             session: sessionmaker = sync_session, ):
    tables_models = [table_model.__table__ for table_model in tables_models]
    with session().connection() as connection:
        Base.metadata.create_all(bind=connection, tables=tables_models)
        connection.commit()
    # print('created')
    ...

def drop_tables_from_models(tables_models: list[type[DeclarativeBase]],
                            session: sessionmaker = sync_session, ):
    tables_models = [table_model.__table__ for table_model in tables_models]
    with session().connection() as connection:
        Base.metadata.drop_all(bind=connection, tables=tables_models)
        connection.commit()
    # print('dropped')
