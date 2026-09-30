from typing import TypedDict, Any

class Parser_output(TypedDict):
    """
    Описание возвращаемых объектов парсеров.
    """
    tablename: str
    data: list[dict[str, Any]]
