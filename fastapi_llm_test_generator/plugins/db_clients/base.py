from typing import Any, Callable, Union


class BaseDBPlugin:
    def __init__(self, db_url: str, isAsync: bool = False):
        super().__init__()
        self.db_url = db_url
        self.isAsync = isAsync

    def extract_table_names(self, source_code: Union[str, Callable]) -> list[Any]:
        raise NotImplementedError

    def get_table_definitions(self, table_name: str) -> tuple[list[Any]]:
        raise NotImplementedError

    async def get_table_definitions(self, table_name: str) -> tuple[list[Any]]:
        raise NotImplementedError

    def generate_markdown(
        self,
        table_name: str,
        columns: list[Any],
        constraints: list[Any],
        indexes: list[Any],
        *args,
        **kwargs,
    ) -> str:
        raise NotImplementedError
