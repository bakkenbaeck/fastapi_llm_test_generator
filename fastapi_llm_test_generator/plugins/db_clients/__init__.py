import catalogue

db_clients_registry = catalogue.create(
    "db_clients", "db_clients_registry", entry_points=True
)

from .asyncpg import AsyncpgDBPlugin, register_asyncpg_db_plugin
from .psycopg2 import Psycopg2DBPlugin, register_psycopg2_db_plugin
from .use_db_plugin import async_use_db_plugin, use_db_plugin
