from inspect import cleandoc
from pathlib import Path

import pytest

from pyarch.parser import build_import_model

pytest_plugins = ['pytester']


def _yield_project_modules(struct: dict[str, str | dict], current_path: Path):
    for key, value in struct.items():
        path = current_path / key
        match value:
            case dict():
                yield from _yield_project_modules(value, path)
            case str():
                yield path, cleandoc(value)


@pytest.fixture
def arch_root_node(project_structure, mocker):
    """Overrides the fixture from the plugin module."""

    def mock_walk_modules(_):
        return _yield_project_modules(project_structure, Path())

    mocker.patch('pyarch.parser._walk_modules', mock_walk_modules)
    return build_import_model(Path())
