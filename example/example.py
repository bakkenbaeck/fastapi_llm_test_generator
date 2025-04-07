from pathlib import Path

from fastapi_llm_test_generator import FastAPILLMTestGenerator
from fastapi_llm_test_generator.plugins.ai_clients import AnthropicClient
from fastapi_llm_test_generator.plugins.db_clients import Psycopg2DBPlugin

db_instance = Psycopg2DBPlugin(
    db_url="postgresql://"  # add postgres url
)
ai_instance = AnthropicClient(
    ANTHROPIC_API_KEY=""  # add API key here
)


def main():
    generator = FastAPILLMTestGenerator(
        "./example/",
        ai_client_plugin_instance=ai_instance,
        test_directory=Path("./example/tests"),
        db_plugin_instance=db_instance,
    )
    routes = generator()


if __name__ == "__main__":
    main()
