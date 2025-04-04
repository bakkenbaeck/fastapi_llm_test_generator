from typing import Any, Callable, Optional

from pydantic import BaseModel


class CodeResponse(BaseModel):
    content: str
    status: str = "success"
    tokens_used: Optional[int] = None
    response: Optional[Any] = None


class Walker(BaseModel):
    source_code: str
    file_path: str
    route_definition: str  # Acts as an ID for skipping already generated tests
    pydantic_models: Optional[set] = None
    function_calls: Optional[dict[str, Callable]] = None

    table_markdowns: Optional[list[str]] = []
    table_defs: Optional[dict] = {}
