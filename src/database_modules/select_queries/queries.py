from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from src.database_modules.select_queries.misc import *
from src.models.database_models import *


def __select_fns_main_info_query(search_type: str,
                                 value: str, ) -> SELECT_QUERY:
    """
    Генерация core-запроса в БД.
    :param search_type:
    :param value:
    :return:
    """
    if search_type not in ['ogrn', 'inn']:
        raise ValueError(f'search_type parameter expected "ogrn" or "inn" but got "{search_type}".')
    statement = text(f'SELECT * '
                     f'FROM {fns_main_info.__tablename__} '
                     f'WHERE {search_type} = :{search_type};')
    parameters = {search_type: value}
    return SELECT_QUERY(statement=statement, parameters=parameters)


def __select_additional_ovkeds_query(search_type: str,
                                     value: str, ) -> SELECT_QUERY:
    """
    Генерация core-запроса в БД.
    :param search_type:
    :param value:
    :return:
    """
    if search_type not in ['ogrn', 'inn']:
        raise ValueError(f'search_type parameter expected "ogrn" or "inn" but got "{search_type}".')
    statement = text(f'SELECT * '
                     f'FROM {okveds.__tablename__} '
                     f'WHERE {search_type} = :{search_type};')

    parameters = {search_type: value}
    return SELECT_QUERY(statement=statement, parameters=parameters)


def __select_licenses_query(search_type: str,
                            value: str, ) -> SELECT_QUERY:
    """
    Генерация core-запроса в БД.
    :param search_type:
    :param value:
    :return:
    """
    if search_type not in ['ogrn', 'inn']:
        raise ValueError(f'search_type parameter expected "ogrn" or "inn" but got "{search_type}".')
    statement = text(f'SELECT * '
                     f'FROM {licenses.__tablename__} '
                     f'WHERE {search_type} = :{search_type};')

    parameters = {search_type: value}
    return SELECT_QUERY(statement=statement, parameters=parameters)


def __select_sno_ip_query(search_type: str,
                          value: str, ) -> SELECT_QUERY:
    """
    Генерация core-запроса в БД.
    :param search_type:
    :param value:
    :return:
    """
    if search_type not in ['ogrn', 'inn']:
        raise ValueError(f'search_type parameter expected "ogrn" or "inn" but got "{search_type}".')

    statement = text(f'SELECT *'
                     f'FROM {sno.__tablename__} '
                     f'WHERE {search_type} = :{search_type};')
    parameters = {search_type: value}
    return SELECT_QUERY(statement=statement, parameters=parameters)


def __select_sno_ul_query(search_type: str,
                          value: str, ) -> SELECT_QUERY:
    """
    Генерация core-запроса в БД.
    :param search_type:
    :param value:
    :return:
    """
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
    """
    Генерация core-запроса в БД.
    :param search_type:
    :param value:
    :return:
    """
    if search_type not in ['ogrn', 'inn']:
        raise ValueError(f'search_type parameter expected "ogrn" or "inn" but got "{search_type}".')

    # CTE здесь ускоряют запрос в БД и гарантируют, что все данные получены в один момент времени.
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
    """
    Генерация core-запроса в БД.
    :param search_type:
    :param value:
    :return:
    """
    if search_type not in ['ogrn', 'inn']:
        raise ValueError(f'search_type parameter expected "ogrn" or "inn" but got "{search_type}".')

    # CTE здесь ускоряют запрос в БД и гарантируют, что все данные получены в один момент времени.
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



async def select_fns_main_info_by_inn_async(engine: AsyncEngine,
                                            inn: str, ) -> AsyncGenerator:
    async with engine.connect() as connection:
        results = await connection.execute(**__select_fns_main_info_query(search_type='inn', value=inn))
    return fetch_result(results)


async def select_fns_main_info_by_ogrn_async(engine: AsyncEngine,
                                             ogrn: str, ) -> AsyncGenerator:
    async with engine.connect() as connection:
        results = await connection.execute(**__select_fns_main_info_query(search_type='ogrn', value=ogrn))
    return fetch_result(results)


async def select_additional_okveds_by_inn_async(engine: AsyncEngine,
                                                inn: str, ) -> AsyncGenerator:
    async with engine.connect() as connection:
        results = await connection.execute(**__select_additional_ovkeds_query(search_type='inn', value=inn))
    return fetch_result(results)


async def select_additional_okveds_by_ogrn_async(engine: AsyncEngine,
                                                 ogrn: str, ) -> AsyncGenerator:
    async with engine.connect() as connection:
        results = await connection.execute(**__select_additional_ovkeds_query(search_type='ogrn', value=ogrn))
    return fetch_result(results)


async def select_licenses_by_inn_async(engine: AsyncEngine,
                                       inn: str, ) -> AsyncGenerator:
    async with engine.connect() as connection:
        results = await connection.execute(**__select_licenses_query(search_type='inn', value=inn))
    return fetch_result(results)


async def select_licenses_by_ogrn_async(engine: AsyncEngine,
                                        ogrn: str, ) -> AsyncGenerator:
    async with engine.connect() as connection:
        results = await connection.execute(**__select_licenses_query(search_type='ogrn', value=ogrn))
    return fetch_result(results)


async def select_sno_ip_by_inn_async(engine: AsyncEngine,
                                     inn: str, ) -> AsyncGenerator:
    async with engine.connect() as connection:
        results = await connection.execute(**__select_sno_ip_query(search_type='inn', value=inn))
    return fetch_result(results)


async def select_sno_ip_by_ogrn_async(engine: AsyncEngine,
                                      ogrn: str, ) -> AsyncGenerator:
    async with engine.connect() as connection:
        results = await connection.execute(**__select_sno_ip_query(search_type='ogrn', value=ogrn))
    return fetch_result(results)


async def select_sno_ul_by_inn_async(engine: AsyncEngine,
                                     inn: str, ) -> AsyncGenerator:
    async with engine.connect() as connection:
        results = await connection.execute(**__select_sno_ul_query(search_type='inn', value=inn))
    return fetch_result(results)


async def select_sno_ul_by_ogrn_async(engine: AsyncEngine,
                                      ogrn: str, ) -> AsyncGenerator:
    async with engine.connect() as connection:
        results = await connection.execute(**__select_sno_ul_query(search_type='ogrn', value=ogrn))
    return fetch_result(results)


async def select_full_data_ip_by_inn_async(engine: AsyncEngine,
                                           inn: str, ) -> AsyncGenerator:
    async with engine.connect() as connection:
        results = await connection.execute(**__select_full_data_ip_query(search_type='inn', value=inn))
    return fetch_result(results)


async def select_full_data_ip_by_ogrn_async(engine: AsyncEngine,
                                            ogrn: str,) -> AsyncGenerator:
    async with engine.connect() as connection:
        results = await connection.execute(**__select_full_data_ip_query(search_type='ogrn', value=ogrn))
    return fetch_result(results)


async def select_full_data_ul_by_inn_async(engine: AsyncEngine,
                                           inn: str, ) -> AsyncGenerator:
    # Конкретно здесь используется генерация запроса как для ИП, тк ОГРН ЮЛ у таблицы с СНО отсутствует
    # и для него нужен отличный запрос.
    async with engine.connect() as connection:
        results = await connection.execute(**__select_full_data_ip_query(search_type='inn', value=inn))
    return fetch_result(results)


async def select_full_data_ul_by_ogrn_async(engine: AsyncEngine,
                                            ogrn: str, ) -> AsyncGenerator:
    async with engine.connect() as connection:
        results = await connection.execute(**__select_full_data_ul_query(search_type='ogrn', value=ogrn))
    return fetch_result(results)


__all__ = ['select_sno_ul_by_ogrn_async', 'select_sno_ul_by_inn_async', 'select_sno_ip_by_ogrn_async',
           'select_full_data_ip_by_inn_async', 'select_full_data_ul_by_inn_async', 'select_full_data_ul_by_ogrn_async',
           'select_full_data_ip_by_ogrn_async', 'select_licenses_by_ogrn_async', 'select_licenses_by_inn_async',
           'select_sno_ip_by_inn_async', 'select_additional_okveds_by_inn_async', 'select_additional_okveds_by_ogrn_async',
           'select_fns_main_info_by_inn_async', 'select_fns_main_info_by_ogrn_async', ]