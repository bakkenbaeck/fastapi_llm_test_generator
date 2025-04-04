import catalogue

ai_clients_registry = catalogue.create(
    "ai_clients", "ai_clients_registry", entry_points=True
)

from .anthropic_client import AnthropicClient, register_anthropic_client
