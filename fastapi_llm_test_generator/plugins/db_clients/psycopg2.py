import inspect
import re
from typing import Any, Callable, Union

from . import db_clients_registry
from .base import BaseDBPlugin

SQL_TABLE_REGEX = r"\b(?:FROM|JOIN|INTO|UPDATE)\s+([a-zA-Z_][a-zA-Z0-9_]*)\b(?!\s*\()"


import logging

logger = logging.getLogger(__name__)


class Psycopg2DBPlugin(BaseDBPlugin):
    def __init__(self, db_url, isAsync=False):
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
            markdown_output += f"| {' | '.join(map(str, col))} |\n"

        markdown_output += "\n## Constraints\n"
        markdown_output += "| Constraint Name | Type | Column |\n"
        markdown_output += "|----------------|------|--------|\n"
        for con in constraints:
            markdown_output += f"| {' | '.join(map(str, con))} |\n"

        markdown_output += "\n## Indexes\n"
        markdown_output += "| Index Name | Definition |\n"
        markdown_output += "|------------|------------|\n"
        for idx in indexes:
            markdown_output += f"| {' | '.join(map(str, idx))} |\n"

        return markdown_output

    def get_table_definitions(self, table_name: str) -> tuple:
        try:
            import psycopg2

            conn = psycopg2.connect(self.db_url)

            cur = conn.cursor()
            cur.execute(
                """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = %s;
            """,
                (table_name,),
            )
            columns = cur.fetchall()

            # Constraints
            cur.execute(
                """
            SELECT conname AS constraint_name, contype AS constraint_type, a.attname AS column_name
            FROM   pg_constraint c
            JOIN   pg_attribute a ON a.attnum = ANY(c.conkey) AND a.attrelid = c.conrelid
            WHERE  c.conrelid = %s::regclass;
            """,
                (table_name,),
            )
            constraints = cur.fetchall()

            # Indexes
            cur.execute(
                """
            SELECT indexname, indexdef
            FROM   pg_indexes
            WHERE  tablename = %s;
            """,
                (table_name,),
            )
            indexes = cur.fetchall()

            cur.close()
            conn.close()

            return columns, constraints, indexes

        except Exception as e:
            logger.warning(f"Could not setup database. Is psycopg2 installed ?: {e}")
            raise e


@db_clients_registry.register("psycopg2")
def register_psycopg2_db_plugin(db_url: str):
    return Psycopg2DBPlugin(db_url=db_url)
