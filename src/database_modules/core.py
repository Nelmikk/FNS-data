from typing import Generator, Any, AsyncGenerator


from src.database_modules.database_sessions import (async_engine, sync_engine,
                                                    async_engine_select_user, )
from src.database_modules.database_misc import batch_data, fetch_result, divide_output, SELECT_QUERY
from src.models.database_models import models_dict, Base, fns_main_info, okveds, sno, licenses, relevant_okveds

from sqlalchemy import insert, inspect, text, Row, TextClause
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.engine.base import Engine



@batch_data(batch_size=14_000)
async def insert_data_async(tablename: str,
                            values: list[dict],
                            engine: AsyncEngine = async_engine, ) -> None:
    async with engine.connect() as connection:
        query = insert(models_dict[tablename].__table__)
        await connection.execute(query, values)
        await connection.commit()

@batch_data(batch_size=14_000)
def insert_data(tablename: str,
                values: list[dict],
                engine: Engine = sync_engine, ) -> None:
    with engine.connect() as connection:
        query = insert(models_dict[tablename].__table__)
        connection.execute(query, values)
        connection.commit()


def __select_fns_main_info_query(search_type: str,
                                 value: str, ) -> SELECT_QUERY:
    if search_type not in ['ogrn', 'inn']:
        raise ValueError(f'search_type parameter expected "ogrn" or "inn" but got "{search_type}".')
    statement = text(f'SELECT * '
                 f'FROM {fns_main_info.__tablename__} '
                 f'WHERE {search_type} = :{search_type};')
    parameters = {search_type: value}
    return SELECT_QUERY(statement=statement, parameters=parameters)


def __select_additional_ovkeds_query(search_type: str,
                                     value: str, ) -> SELECT_QUERY:
    if search_type not in ['ogrn', 'inn']:
        raise ValueError(f'search_type parameter expected "ogrn" or "inn" but got "{search_type}".')
    statement = text(f'SELECT * '
                        f'FROM {okveds.__tablename__} '
                        f'WHERE {search_type} = :{search_type};')

    parameters = {search_type: value}
    return SELECT_QUERY(statement=statement, parameters=parameters)


def __select_licenses_query(search_type: str,
                            value: str, ) -> SELECT_QUERY:
    if search_type not in ['ogrn', 'inn']:
        raise ValueError(f'search_type parameter expected "ogrn" or "inn" but got "{search_type}".')
    statement = text(f'SELECT * '
                        f'FROM {licenses.__tablename__} '
                        f'WHERE {search_type} = :{search_type};')

    parameters = {search_type: value}
    return SELECT_QUERY(statement=statement, parameters=parameters)


def __select_sno_ip_query(search_type: str,
                          value: str, ) -> SELECT_QUERY:
    if search_type not in ['ogrn', 'inn']:
        raise ValueError(f'search_type parameter expected "ogrn" or "inn" but got "{search_type}".')

    statement = text(f'SELECT *'
                     f'FROM {sno.__tablename__} '
                     f'WHERE {search_type} = :{search_type};')
    parameters = {search_type: value}
    return SELECT_QUERY(statement=statement, parameters=parameters)


def __select_sno_ul_query(search_type: str,
                          value: str, ) -> SELECT_QUERY:
    if search_type not in ['ogrn', 'inn']:
        raise ValueError(f'search_type parameter expected "ogrn" or "inn" but got "{search_type}".')

    statement = text(f'SELECT {fns_main_info.__tablename__}.inn, {fns_main_info.__tablename__}.ogrn, '
                     f'{sno.__tablename__}.eshn, {sno.__tablename__}.usn, {sno.__tablename__}.ausn, '
                     f'{sno.__tablename__}.srp, {sno.__tablename__}.psn, {sno.__tablename__}.npd '
                     f'FROM {fns_main_info.__tablename__} '
                     f'INNER JOIN {sno.__tablename__} ON {sno.__tablename__}.inn = {fns_main_info.__tablename__}.inn '
                     f'WHERE {fns_main_info.__tablename__}.{search_type} = :{search_type};')

    parameters = {search_type: value}
    return SELECT_QUERY(statement=statement, parameters=parameters)


def __select_full_data_ip_query(search_type: str,
                                value: str, ) -> SELECT_QUERY:
    if search_type not in ['ogrn', 'inn']:
        raise ValueError(f'search_type parameter expected "ogrn" or "inn" but got "{search_type}".')

    statement = text(f'WITH {sno.__tablename__}_cte AS ('
                        f'SELECT * '
                        f'FROM {sno.__tablename__} '
                        f'WHERE {search_type} = :{search_type}'
                     f'), '
                     f'{okveds.__tablename__}_cte AS ('
                        f'SELECT * '
                        f'FROM {okveds.__tablename__} '
                        f'WHERE {search_type} = :{search_type}'
                     f'),'
                     f'{licenses.__tablename__}_cte AS ('
                        f'SELECT * '
                        f'FROM {licenses.__tablename__} '
                        f'WHERE {search_type} = :{search_type}'
                     f')'
                     f'SELECT {fns_main_info.__tablename__}.*'
                     f', {licenses.__tablename__}_cte.licenses_data'
                     f', {okveds.__tablename__}_cte.additional_okveds_data'
                     f', {sno.__tablename__}_cte.eshn, {sno.__tablename__}_cte.usn, {sno.__tablename__}_cte.ausn'
                     f', {sno.__tablename__}_cte.srp, {sno.__tablename__}_cte.psn, {sno.__tablename__}_cte.npd '
                     f'FROM {fns_main_info.__tablename__} '
                     f'LEFT JOIN {sno.__tablename__}_cte ON {sno.__tablename__}_cte.ogrn = {fns_main_info.__tablename__}.ogrn '
                     f'LEFT JOIN {okveds.__tablename__}_cte ON {okveds.__tablename__}_cte.ogrn = {fns_main_info.__tablename__}.ogrn '
                     f'LEFT JOIN {licenses.__tablename__}_cte ON {licenses.__tablename__}_cte.ogrn = {fns_main_info.__tablename__}.ogrn '
                     f'WHERE {fns_main_info.__tablename__}.{search_type} = :{search_type};')
    parameters = {search_type: value}
    return SELECT_QUERY(statement=statement, parameters=parameters)


def __select_full_data_ul_query(search_type: str,
                                value: str, ) -> SELECT_QUERY:
    if search_type not in ['ogrn', 'inn']:
        raise ValueError(f'search_type parameter expected "ogrn" or "inn" but got "{search_type}".')

    statement = text(f'WITH {sno.__tablename__}_cte AS ('
                        f'SELECT * '
                        f'FROM {sno.__tablename__} '
                        f'WHERE inn = (SELECT inn FROM {fns_main_info.__tablename__} '
                            f'WHERE {fns_main_info.__tablename__}.ogrn = :{search_type})'
                     f'), '
                     
                     f'{okveds.__tablename__}_cte AS ('
                        f'SELECT * '
                        f'FROM {okveds.__tablename__} '
                        f'WHERE {search_type} = :{search_type}'
                     f'), '
                     
                     f'{licenses.__tablename__}_cte AS ('
                        f'SELECT * '
                        f'FROM {licenses.__tablename__} '
                        f'WHERE {search_type} = :{search_type}'
                     f') '
                     
                     f'SELECT {fns_main_info.__tablename__}.*'
                     f', {licenses.__tablename__}_cte.licenses_data'
                     f', {okveds.__tablename__}_cte.additional_okveds_data'
                     f', {sno.__tablename__}_cte.eshn, {sno.__tablename__}_cte.usn, {sno.__tablename__}_cte.ausn'
                     f', {sno.__tablename__}_cte.srp, {sno.__tablename__}_cte.psn, {sno.__tablename__}_cte.npd '
                     f'FROM {fns_main_info.__tablename__} '
                     f'LEFT JOIN {sno.__tablename__}_cte ON {sno.__tablename__}_cte.inn = {fns_main_info.__tablename__}.inn '
                     f'LEFT JOIN {okveds.__tablename__}_cte ON {okveds.__tablename__}_cte.ogrn = {fns_main_info.__tablename__}.ogrn '
                     f'LEFT JOIN {licenses.__tablename__}_cte ON {licenses.__tablename__}_cte.ogrn = {fns_main_info.__tablename__}.ogrn '
                     f'WHERE {fns_main_info.__tablename__}.{search_type} = :{search_type};')
    parameters = {search_type: value}
    return SELECT_QUERY(statement=statement, parameters=parameters)


async def select_fns_main_info_by_inn_async(inn: str,
                                            engine: AsyncEngine = async_engine_select_user, ) -> AsyncGenerator:

    async with engine.connect() as connection:
        results = await connection.execute(**__select_fns_main_info_query(search_type='inn', value=inn))

    return fetch_result(results)



async def select_fns_main_info_by_ogrn_async(ogrn: str,
                                             engine: AsyncEngine = async_engine_select_user, ) -> AsyncGenerator:

    async with engine.connect() as connection:
        results = await connection.execute(**__select_fns_main_info_query(search_type='ogrn', value=ogrn))

    return fetch_result(results)



async def select_additional_okveds_by_inn_async(inn: str,
                                                engine: AsyncEngine = async_engine_select_user, ) -> AsyncGenerator:

    async with engine.connect() as connection:
        results = await connection.execute(**__select_additional_ovkeds_query(search_type='inn', value=inn))

    return fetch_result(results)



async def select_additional_okveds_by_ogrn_async(ogrn: str,
                                                 engine: AsyncEngine = async_engine_select_user, ) -> AsyncGenerator:

    async with engine.connect() as connection:
        results = await connection.execute(**__select_additional_ovkeds_query(search_type='ogrn', value=ogrn))

    return fetch_result(results)


async def select_licenses_by_inn_async(inn: str,
                                       engine: AsyncEngine = async_engine_select_user, ) -> AsyncGenerator:
    async with engine.connect() as connection:
        results = await connection.execute(**__select_licenses_query(search_type='inn', value=inn))

    return fetch_result(results)


async def select_licenses_by_ogrn_async(ogrn: str,
                                        engine: AsyncEngine = async_engine_select_user, ) -> AsyncGenerator:
    async with engine.connect() as connection:
        results = await connection.execute(**__select_licenses_query(search_type='ogrn', value=ogrn))

    return fetch_result(results)


async def select_sno_ip_by_inn_async(inn: str,
                                     engine: AsyncEngine = async_engine_select_user, ) -> AsyncGenerator:

    async with engine.connect() as connection:
        results = await connection.execute(**__select_sno_ip_query(search_type='inn', value=inn))

    return fetch_result(results)


async def select_sno_ip_by_ogrn_async(ogrn: str,
                                      engine: AsyncEngine = async_engine_select_user, ) -> AsyncGenerator:

    async with engine.connect() as connection:
        results = await connection.execute(**__select_sno_ip_query(search_type='ogrn', value=ogrn))

    return fetch_result(results)


async def select_sno_ul_by_inn_async(inn: str,
                                     engine: AsyncEngine = async_engine_select_user, ):

    async with engine.connect() as connection:
        results = await connection.execute(**__select_sno_ul_query(search_type='inn', value=inn))

    return fetch_result(results)


async def select_sno_ul_by_ogrn_async(ogrn: str,
                                      engine: AsyncEngine = async_engine_select_user, ) -> AsyncGenerator:
    async with engine.connect() as connection:
        results = await connection.execute(**__select_sno_ul_query(search_type='ogrn', value=ogrn))

    return fetch_result(results)


async def select_full_data_ip_by_inn_async(inn: str,
                                     engine: AsyncEngine = async_engine_select_user, ) -> AsyncGenerator:
    async with engine.connect() as connection:
        results = await connection.execute(**__select_full_data_ip_query(search_type='inn', value=inn))
    return fetch_result(results)

async def select_full_data_ip_by_ogrn_async(ogrn: str,
                                      engine: AsyncEngine = async_engine_select_user, ) -> AsyncGenerator:
    async with engine.connect() as connection:
        results = await connection.execute(**__select_full_data_ip_query(search_type='ogrn', value=ogrn))
    return fetch_result(results)


async def select_full_data_ul_by_inn_async(inn: str,
                                           engine: AsyncEngine = async_engine_select_user, ) -> AsyncGenerator:
    async with engine.connect() as connection:
        results = await connection.execute(**__select_full_data_ip_query(search_type='inn', value=inn))
    return fetch_result(results)

async def select_full_data_ul_by_ogrn_async(ogrn: str,
                                            engine: AsyncEngine = async_engine_select_user, ) -> AsyncGenerator:
    async with engine.connect() as connection:
        results = await connection.execute(**__select_full_data_ul_query(search_type='ogrn', value=ogrn))
    return fetch_result(results)


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