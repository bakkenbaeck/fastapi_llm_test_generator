import json
import logging
from pathlib import Path
from typing import Union

import typer
from catalogue import Registry
from rich.progress import Progress, SpinnerColumn, TextColumn
from typer.main import get_command
from typing_extensions import Annotated

from .logging import setup_logging
from .plugins import ai_clients_registry, db_clients_registry
from .walk_ast import FastAPILLMTestGenerator

logger = logging.getLogger(__name__)

NAME = "fastapi_llm_test_generator"
HELP = """fastapi_llm_test_generator Command-line Interface"""
COMMAND = "python -m fastapi_llm_test_generator"

app = typer.Typer(name=NAME, help=HELP, rich_markup_mode="rich")


def load_plugin(registry: Registry, plugin: str = None):
    if plugin not in registry.get_all().keys():
        raise Exception(f"{plugin} not in {registry.namespace[0]} registery")
    logger.debug(f"loading plugin: {plugin}")
    return registry.get(plugin)


@app.command()
def generate(
    source_app_directory: Annotated[
        Path, typer.Argument(help="Path to the FastAPI app directory")
    ],
    client_plugin: Annotated[
        str, typer.Argument(help="Name of the AI client plugin to use")
    ],
    config_file: Annotated[Path, typer.Option(help="Path to a config file")] = None,
    test_directory: Annotated[
        Path,
        typer.Argument(
            help="Path to the tests app directory if none provided it will be create at source_app_directory/tests"
        ),
    ] = Path("./tests"),
    db_plugin: Annotated[
        Union[str, None],
        typer.Option(help="Optional database plugin to enable DB integration"),
    ] = None,
    function_name: Annotated[
        Union[str, None],
        typer.Option(help="Target function name to generate tests for"),
    ] = None,
    route_path: Annotated[
        Union[str, None],
        typer.Option(help="Filter routes matching this path or subpath"),
    ] = None,
    db_url: Annotated[
        Union[str, None], typer.Option(help="Database URL used by the DB plugin")
    ] = None,
    api_key: Annotated[
        Union[str, None], typer.Option(help="API key for the selected AI client plugin")
    ] = None,
    model: Annotated[
        Union[str, None], typer.Option(help="LLM model name to use for test generation")
    ] = None,
    additional_prompt_pre: Annotated[
        Union[str, None],
        typer.Option(help="Prompt text to prepend before the main content"),
    ] = None,
    additional_prompt_info: Annotated[
        Union[str, None],
        typer.Option(help="Prompt text to insert as additional context"),
    ] = None,
    mock_prompt: Annotated[
        Union[str, None],
        typer.Option(help="Prompt describing mocks"),
    ] = None,
    fixtures_prompt: Annotated[
        Union[str, None],
        typer.Option(help="Prompt describing fixtures"),
    ] = None,
    additional_prompt_after: Annotated[
        Union[str, None],
        typer.Option(help="Prompt text to append after the main content"),
    ] = None,
    prompt_type: Annotated[
        str, typer.Option(help="Format/type of prompt to use (e.g., pytest)")
    ] = "pytest",
    overwrite: Annotated[
        bool,
        typer.Option(
            help="Whether to overwrite existing tests, otherwise it will skip"
        ),
    ] = False,
    run_tests: Annotated[
        bool,
        typer.Option(
            help="Run tests with pytest - this might fail due to insufficient config. Be careful!"
        ),
    ] = False,
):
    config = {}

    if config_file and config_file.is_file():
        config = json.loads(config_file.read_text())

    db_plugin = db_plugin or config.get("db_plugin", None)

    function_name = function_name or config.get("function_name", None)
    route_path = route_path or config.get("route_path", None)
    db_url = db_url or config.get("db_url", None)
    api_key = api_key or config.get("api_key")
    model = model or config.get("model", None)
    additional_prompt_pre = additional_prompt_pre or config.get(
        "additional_prompt_pre", None
    )
    additional_prompt_info = additional_prompt_info or config.get(
        "additional_prompt_info", None
    )
    mock_prompt = mock_prompt or config.get("mock_prompt", None)
    fixtures_prompt = fixtures_prompt or config.get("fixtures_prompt", None)
    additional_prompt_after = additional_prompt_after or config.get(
        "additional_prompt_after", None
    )
    prompt_type = prompt_type or config.get("prompt_type", None)
    overwrite = overwrite or config.get("overwrite", False)
    run_tests = run_tests or config.get("run_tests", False)

    db_plugin_instance = None
    if db_plugin:
        db_plugin_func = load_plugin(db_clients_registry, plugin=db_plugin)
        if db_plugin_func and db_url is None:
            typer.echo("Error: DB Plugin requires --db_url")
            raise typer.Exit(1)
        db_plugin_instance = db_plugin_func(db_url)

    ai_client_plugin_func = load_plugin(ai_clients_registry, plugin=client_plugin)
    if ai_client_plugin_func and api_key is None:
        typer.echo("Error: Client Plugin requires --api_key")
        raise typer.Exit(1)
    ai_client_plugin_instance = ai_client_plugin_func(api_key, model)

    generator = FastAPILLMTestGenerator(
        source_app_directory,
        ai_client_plugin_instance,
        test_directory,
        db_plugin_instance,
        function_name,
        route_path,
        additional_prompt_pre,
        additional_prompt_info,
        mock_prompt,
        fixtures_prompt,
        additional_prompt_after,
        prompt_type,
        overwrite,
        run_tests,
    )
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Generating...", total=None)
        return generator()


@app.callback()
def callback(
    verbose: bool = typer.Option(False, help="Enable verbose output"),
) -> None:
    """
    Show me some info
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    setup_logging(level=log_level)


def setup_cli() -> None:
    # Make sure the entry-point for CLI runs, so that they get imported.
    db_clients_registry.get_all()
    ai_clients_registry.get_all()

    # Ensure that the help messages always display the correct prompt
    command = get_command(app)
    command(prog_name=COMMAND)
