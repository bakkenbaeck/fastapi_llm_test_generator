from pathlib import Path

from fastapi_llm_test_generator import generate
from fastapi_llm_test_generator.plugins.ai_clients import AnthropicClient
from fastapi_llm_test_generator.plugins.db_clients import Psycopg2DBPlugin

db_instance = Psycopg2DBPlugin(
    db_url="postgresql://"
)
ai_instance = AnthropicClient(
    ANTHROPIC_API_KEY=""
)


def main():
    generate(
        "./example/",
        ai_client_plugin_instance=ai_instance,
        test_directory=Path("./example/tests"),
        db_plugin_instance=db_instance,
    )


if __name__ == "__main__":
    main()
