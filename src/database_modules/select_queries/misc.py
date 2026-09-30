from sqlalchemy.engine import CursorResult
from sqlalchemy import TextClause

from typing import TypedDict, AsyncGenerator



async def fetch_result(results: CursorResult, ) -> AsyncGenerator:
    """
    Генератор ответа данных БД.
        Проходит по всем элементам ответа БД и генерирует словари для моделей АПИ.
    :param results:
    :return:
    """
    keys = results.keys()._keys
    for result in results.fetchall():
        yield {k: v for k, v in zip(keys, result) if k != 'id'}

class SELECT_QUERY(TypedDict):
    """
    Структура данных для запросов в БД через AsyncEngine/Engine.
    """
    statement: TextClause
    parameters: dict[str, str]