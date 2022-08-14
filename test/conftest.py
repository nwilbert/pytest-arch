from inspect import cleandoc
from pathlib import Path
from typing import Callable

import pytest

from pyarch.model import DotPath, Node
from pyarch.parser import build_import_model
from pyarch.testutil import Package

pytest_plugins = 'pytester'


def _yield_project_modules(struct: dict[str, str | dict], current_path: Path):
    for key, value in struct.items():
        path = current_path / key
        match value:
            case dict():
                yield from _yield_project_modules(value, path)
            case str():
                yield path, cleandoc(value)


@pytest.fixture
def project_base_node(project_structure, mocker):
    def mock_walk_modules(_):
        return _yield_project_modules(project_structure, Path())

    mocker.patch('pyarch.parser._walk_modules', mock_walk_modules)
    return build_import_model(Path())


@pytest.fixture
def package(project_base_node: Node) -> Callable[[str], Package]:
    def _create_package(path: str) -> Package:
        node = project_base_node.get(DotPath(path))
        if not node:
            raise KeyError(f'Found no node for path {path} in project.')
        return Package(node)

    return _create_package
