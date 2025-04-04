import logging

from catalogue import Registry

from .ai_clients import AnthropicClient, ai_clients_registry
from .db_clients import AsyncpgDBPlugin, Psycopg2DBPlugin, db_clients_registry

logger = logging.getLogger(__name__)


def load_plugin(registry: Registry, plugin: str = None):
    if plugin not in registry.get_all().keys():
        raise Exception(f"{plugin} not in {registry.namespace[0]} registery")
    logger.debug(f"using plugin: {plugin}")
    return registry.get(plugin)
