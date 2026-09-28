from typing import TypedDict, Any

class Parser_output(TypedDict):
    tablename: str
    data: list[dict[str, Any]]
