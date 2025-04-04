import inspect
import re
from typing import Any, Callable, Union

from . import db_clients_registry
from .base import BaseDBPlugin

SQL_TABLE_REGEX = r"\b(?:FROM|JOIN|INTO|UPDATE)\s+([a-zA-Z_][a-zA-Z0-9_]*)\b(?!\s*\()"
import typer

app = typer.Typer()


class AsyncpgDBPlugin(BaseDBPlugin):
    def __init__(self, db_url, isAsync=True):
        super().__init__(db_url, isAsync)

    def extract_table_names(self, source_code: Union[str, Callable]) -> list[Any]:
        if callable(source_code):
            source_code = inspect.getsource(source_code)
        source_code = re.sub(r"^\s*import.*\n", "", source_code, flags=re.MULTILINE)
        source_code = re.sub(
            r"^\s*from\s+[^\n]+\s+import.*\n", "", source_code, flags=re.MULTILINE
        )

        # Find table names in SQL queries
        return re.findall(SQL_TABLE_REGEX, source_code, re.IGNORECASE)

    def generate_markdown(self, table_name, columns, constraints, indexes):
        # Generate Markdown
        markdown_output = f"# Table: `{table_name}`\n\n"

        markdown_output += "## Columns\n"
        markdown_output += "| Column | Type | Nullable | Default |\n"
        markdown_output += "|--------|------|----------|---------|\n"
        for col in columns:
            markdown_output += f"| {col['column_name']} | {col['data_type']} | {col['is_nullable']} | {col['column_default']} |\n"

        markdown_output += "\n## Constraints\n"
        markdown_output += "| Constraint Name | Type | Column |\n"
        markdown_output += "|----------------|------|--------|\n"
        for con in constraints:
            markdown_output += f"| {con['constraint_name']} | {con['constraint_type']} | {con['column_name']} |\n"

        markdown_output += "\n## Indexes\n"
        markdown_output += "| Index Name | Definition |\n"
        markdown_output += "|------------|------------|\n"
        for idx in indexes:
            markdown_output += f"| {idx['indexname']} | {idx['indexdef']} |\n"
        return markdown_output

    async def get_table_definitions(self, table_name: str) -> tuple:
        try:
            import asyncpg

            async with asyncpg.create_pool(dsn=self.db_url) as pool:
                async with pool.acquire() as conn:
                    column_query = """SELECT column_name, data_type, is_nullable, column_default
                            FROM information_schema.columns
                            WHERE table_name = $1;"""
                    columns = await conn.fetch(column_query, table_name)

                    constraint_query = """SELECT conname AS constraint_name, contype AS constraint_type, 
                        a.attname AS column_name
                    FROM   pg_constraint c
                    JOIN   pg_attribute a ON a.attnum = ANY(c.conkey) AND a.attrelid = c.conrelid
                    WHERE  c.conrelid = $1::regclass;"""
                    constraints = await conn.fetch(constraint_query, table_name)

                    index_query = """SELECT indexname, indexdef
                    FROM   pg_indexes
                    WHERE  tablename = $1;"""
                    indexes = await conn.fetch(index_query, table_name)

                return columns, constraints, indexes

        except Exception as e:
            print("Could not setup database. Is asyncpg installed ?")
            raise e


@db_clients_registry.register("asyncpg")
def register_asyncpg_db_plugin(db_url: str):
    return AsyncpgDBPlugin(db_url=db_url)
