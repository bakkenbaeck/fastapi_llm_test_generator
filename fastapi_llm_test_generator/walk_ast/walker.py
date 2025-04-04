import ast
import inspect
import logging
import sys
import typing
from pathlib import Path
from typing import Callable

from pydantic import BaseModel

from fastapi_llm_test_generator.llm import make_prompt
from fastapi_llm_test_generator.plugins.db_clients import async_use_db_plugin, use_db_plugin
from fastapi_llm_test_generator.schemas import Walker

from .fastapi_functions import (
    find_fastapi_app,
    load_fastapi_app,
    load_fastapi_module,
)
from .utils import run_test

logger = logging.getLogger(__name__)


def get_pydantic_models_from_function(func: Callable, route: Callable = None) -> set:
    """Extracts all/only Pydantic models used in a function."""
    models = set()
    hints = typing.get_type_hints(func)

    # Get type hints
    for hint in hints.values():
        if hasattr(hint, "__origin__"):
            for arg in hint.__args__:
                if inspect.isclass(arg) and issubclass(arg, BaseModel):
                    models.add(arg)
        elif inspect.isclass(hint) and issubclass(hint, BaseModel):
            models.add(hint)

    # Get type hints for return type
    return_type = hints.get("return")
    if (
        return_type
        and inspect.isclass(return_type)
        and issubclass(return_type, BaseModel)
    ):
        models.add(return_type)

    # Check if route has a response model
    if route and hasattr(route, "response_model"):
        response_model = route.response_model
        if hasattr(response_model, "__origin__"):  # Union[Model, List[Model]]
            for arg in response_model.__args__:
                if inspect.isclass(arg) and issubclass(arg, BaseModel):
                    models.add(arg)
        elif inspect.isclass(response_model) and issubclass(response_model, BaseModel):
            models.add(response_model)

    # TODO dependencies ?

    return models


# TODO Make this better
def is_user_defined(func_obj: Callable) -> bool:
    """Check if the function belongs to a user-defined module."""
    if not hasattr(func_obj, "__module__"):
        return False  # Ignore built-in functions

    module_name = func_obj.__module__
    if module_name is None:
        return False

    if module_name in [
        "__builtin__",
        "builtins",
        "sys",
        "os",
        "importlib",
        "collections",
        "math",
    ]:
        return False

    if "site-packages" in module.__file__:
        return False

    if "lib" in module.__file__:
        return False

    if ".venv" in module.__file__:
        return False

    # Standard library and installed packages are in sys.modules but have __file__ attributes
    module = sys.modules.get(module_name)
    if module and hasattr(module, "__file__"):
        cls = getattr(func_obj, "__qualname__", "").split(".")[0]
        if cls in func_obj.__globals__:
            cls_obj = func_obj.__globals__[cls]
            if inspect.isclass(cls_obj) and issubclass(cls_obj, BaseModel):
                return False  # Exclude Pydantic models

    return True


def walk_tree(func: Callable, visited=None) -> dict[str, Callable]:
    """Extract all function calls made inside the given function's source code."""
    if visited is None:
        visited = set()

    if func in visited:
        return {}

    visited.add(func)

    source_code = inspect.getsource(func)
    tree = ast.parse(source_code)
    function_calls = {}

    class CallVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            if isinstance(node.func, ast.Name):  # Direct function calls
                func_name = node.func.id
            elif isinstance(
                node.func, ast.Attribute
            ):  # Method calls (e.g., obj.method())
                func_name = ast.unparse(node.func)
            else:
                self.generic_visit(node)
                return
            try:
                func_obj = eval(func_name, func.__globals__)  # Get function object
                if callable(func_obj):
                    if is_user_defined(func_obj):
                        print("is_user_defined", func_obj)
                        # "user" functions
                        function_calls[func_name] = func_obj
                        function_calls.update(walk_tree(func_obj, visited))
                    else:
                        # external functions
                        pass
            except Exception:
                pass  # Ignore if function is built-in or unavailable

            self.generic_visit(node)

    CallVisitor().visit(tree)

    return function_calls


def inspect_fastapi_route(route):
    if hasattr(route, "endpoint") and hasattr(route, "methods"):
        func = route.endpoint

        # 1. get route source code
        source_code = inspect.getsource(func)
        file_path = inspect.getfile(func)

        # 2. get pydantic models from
        pydantic_models = get_pydantic_models_from_function(func, route)

        # 3. get nested functions
        function_calls = walk_tree(func)

        # 4. and their pydantic model definitions
        for name, func in function_calls.items():
            models = get_pydantic_models_from_function(func)
            pydantic_models.update(models)

        return Walker(
            source_code=source_code,
            file_path=file_path,
            route_definition=f"{route.path}_{route.methods}",
            pydantic_models=pydantic_models,
            function_calls=function_calls,
        )


def walker(
    source_app_directory,
    test_directory: Path = None,
    function_name=None,
    route_path=None,
    db_plugin_instance=None,
    ai_client_plugin_instance=None,
    additional_prompt_pre: str = None,
    additional_prompt_info: str = None,
    mock_prompt: str = None,
    fixtures_prompt: str = None,
    additional_prompt_after: str = None,
    prompt_type: str = None,
    overwrite: bool = False,
    run_tests: bool = False,
) -> list[Walker]:
    app_file_path, app_function_name = find_fastapi_app(source_app_directory)
    if not app_file_path:
        raise Exception("No FastAPI app found.")

    if db_plugin_instance and db_plugin_instance.isAsync:
        import asyncio

    module, spec = load_fastapi_module(app_file_path)
    routes = []
    # try:
    spec.loader.exec_module(module)
    app = load_fastapi_app(module, app_function_name)
    logger.info("Generating tests")

    filtered_routes = [
        route
        for route in app.routes
        if (
            (
                function_name
                and route_path
                and route.name == function_name
                and route_path in route.path
            )
            or (function_name and not route_path and route.name == function_name)
            or (not function_name and route_path and route_path in route.path)
        )
        and not (
            "/openapi.json" in route.path
            or "/docs" in route.path
            or "/redoc" in route.path
            or route.path
            == "/static"  # TODO check for other static ONLY true endpoints
        )
    ]

    if not test_directory.exists():
        test_directory = Path(source_app_directory) / "tests"
        test_directory.mkdir()

    for index, route in enumerate(filtered_routes):
        logger.debug(f"{index}/{len(filtered_routes)}")

        if test_directory.exists():
            route_parts = route.path.strip("/").split("/")
            method_suffix = "_".join(route.methods).upper()
            directory = test_directory / Path(*route_parts)
            if not directory.exists():
                directory.mkdir(parents=True)

            file_name = directory / f"test_{'_'.join(route_parts)}_{method_suffix}.py"

        if file_name.exists() and not overwrite:
            logger.info(f"Skipping test '{file_name}' already exists")
            continue

        print(route)

        # 1. get all necessary codes, models, definitions
        res = inspect_fastapi_route(route)

        # 2. extract necessary tables
        if db_plugin_instance and db_plugin_instance.isAsync:
            # TODO ehm this is not so good :(
            res = asyncio.run(async_use_db_plugin(db_plugin_instance, res))
        elif db_plugin_instance:
            res = use_db_plugin(db_plugin_instance, res)
        else:
            logger.debug("Not using db_plugin")

        # 4. create prompt
        prompt = make_prompt(
            additional_prompt_pre=additional_prompt_pre,
            additional_prompt_info=additional_prompt_info,
            mock_prompt=mock_prompt,
            fixtures_prompt=fixtures_prompt,
            url=route.path,
            pydantic_prompt="".join(
                [inspect.getsource(r) for r in res.pydantic_models if print(r) is None]
            )
            if res.pydantic_models
            else None,
            function_prompt="".join(
                [inspect.getsource(r) + "\n" for name, r in res.function_calls.items()]
            )
            if res.function_calls
            else None,
            db_prompt="\n".join(res.table_markdowns) + "\n"
            if res.table_markdowns
            else None,
            code_prompt=res.source_code,
            additional_prompt_after=additional_prompt_after,
            prompt_type=prompt_type,
        )

        logger.debug(prompt)
        # 5. ask llm
        response = ai_client_plugin_instance(prompt)

        with open(file_name, "w") as f:
            f.write(response.content)
        logger.debug(f"Writing file: {file_name}")
        # 6. potentially run tests

        if run_tests:
            run_test(file_name, prompt_type)

        routes.append((res, response))

    # except Exception as e:
    #     print(f"Error loading FastAPI app: {e}")

    return routes
