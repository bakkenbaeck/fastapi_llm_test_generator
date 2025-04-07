import ast
import importlib
import logging
import os
import sys
from pathlib import Path
from typing import Union

import typer

logger = logging.getLogger(__name__)


def load_fastapi_app(module, function_name: str):
    try:
        create_app = getattr(module, function_name, None)
        if callable(create_app):
            app = create_app()
            return app
    except Exception as e:
        raise e


def load_fastapi_module(fastapi_app_file: str):
    module_name = fastapi_app_file.stem
    spec = importlib.util.spec_from_file_location(module_name, fastapi_app_file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    return module, spec


def find_fastapi_app(directory: str) -> Union[Path, None]:
    directory = Path(directory).resolve()
    for root, _, files in os.walk(directory):
        # TODO enumerate more common virtual envs. Or is there another way to do this ?
        if "venv" in root or "env" in root or "site-packages" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=str(file_path))

                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            fastapi_instance = None
                            for stmt in node.body:
                                if isinstance(stmt, ast.Assign):
                                    if (
                                        isinstance(stmt.value, ast.Call)
                                        and isinstance(stmt.value.func, ast.Name)
                                        and stmt.value.func.id == "FastAPI"
                                    ):
                                        fastapi_instance = stmt.targets[0].id
                                # if there is a fastapi instance then this is something like create_app()
                                if isinstance(stmt, ast.Return) and isinstance(
                                    stmt.value, ast.Name
                                ):
                                    if stmt.value.id == fastapi_instance:
                                        return file_path, node.name, None
                                # TODO find other ways e.g. plain old app = FastAPI and also adjust walktree

                        elif isinstance(node, ast.Assign):
                            if isinstance(node.value, ast.Call) and isinstance(
                                node.value.func, ast.Name
                            ):
                                if node.value.func.id == "FastAPI":
                                    fastapi_instance = node.targets[
                                        0
                                    ].id  # Capture the FastAPI instance
                                    return file_path, None, fastapi_instance

                except Exception as e:
                    logger.debug(f"Skipping {file_path}: {e}")
    return None, None, None


if __name__ == "__main__":
    typer.run(find_fastapi_app)
