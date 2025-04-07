from pathlib import Path
from typing import Any, Union

from fastapi_llm_test_generator.schemas import CodeResponse, Walker

from .walker import walker


class FastAPILLMTestGenerator:
    def __init__(
        self,
        source_app_directory: Union[str, Path],
        ai_client_plugin_instance: Any,
        test_directory: Union[str, Path] = None,
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
        self.source_app_directory = source_app_directory
        self.ai_client_plugin_instance = ai_client_plugin_instance
        self.test_directory = test_directory
        self.db_plugin_instance = db_plugin_instance
        self.function_name = function_name
        self.route_path = route_path
        self.additional_prompt_pre = additional_prompt_pre
        self.additional_prompt_info = additional_prompt_info
        self.mock_prompt = mock_prompt
        self.fixtures_prompt = fixtures_prompt
        self.additional_prompt_after = additional_prompt_after
        self.prompt_type = prompt_type
        self.overwrite = overwrite
        self.run_tests = run_tests

    def __call__(self) -> list[tuple[Walker, CodeResponse]]:
        routes = walker(
            self.source_app_directory,
            self.test_directory,
            function_name=self.function_name,
            route_path=self.route_path,
            db_plugin_instance=self.db_plugin_instance,
            ai_client_plugin_instance=self.ai_client_plugin_instance,
            additional_prompt_pre=self.additional_prompt_pre,
            additional_prompt_info=self.additional_prompt_info,
            mock_prompt=self.mock_prompt,
            fixtures_prompt=self.fixtures_prompt,
            additional_prompt_after=self.additional_prompt_after,
            prompt_type=self.prompt_type,
            overwrite=self.overwrite,
            run_tests=self.run_tests,
        )
        return routes
