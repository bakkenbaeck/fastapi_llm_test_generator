from pathlib import Path
from typing import Any

from .walker import walker


def generate(
    source_app_directory,
    ai_client_plugin_instance,
    test_directory: Path = None,
    db_plugin_instance: Any = None,
    function_name: str = None,
    route_path: str = None,
    additional_prompt_pre: str = None,
    additional_prompt_info: str = None,
    mock_prompt: str = None,
    fixtures_prompt: str = None,
    additional_prompt_after: str = None,
    prompt_type: str = "pytest",
    overwrite: bool = None,
    run_tests: bool = None,
):
    routes = walker(
        source_app_directory,
        test_directory,
        function_name=function_name,
        route_path=route_path,
        db_plugin_instance=db_plugin_instance,
        ai_client_plugin_instance=ai_client_plugin_instance,
        additional_prompt_pre=additional_prompt_pre,
        additional_prompt_info=additional_prompt_info,
        mock_prompt=mock_prompt,
        fixtures_prompt=fixtures_prompt,
        additional_prompt_after=additional_prompt_after,
        prompt_type=prompt_type,
        overwrite=overwrite,
        run_tests=run_tests,
    )

    return routes
