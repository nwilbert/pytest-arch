import pathlib
from inspect import cleandoc

import pytest

from pyarch.testutil import Import, Package, Project


def _create_project_structure(
    struct: dict[str, str | dict], current_path: pathlib.Path
):
    for key, value in struct.items():
        path = current_path / key
        match value:
            case dict():
                path.mkdir()
                _create_project_structure(value, path)
            case str():
                path.write_text(cleandoc(value))


@pytest.fixture
def project_on_disk(project_structure, tmp_path):
    _create_project_structure(project_structure, pathlib.Path(tmp_path))
    return tmp_path


# TODO: part of plugin setup
@pytest.fixture
def package():
    # TODO: by default go up until there is an 'src' dir, or a pyproject.toml and read from it
    project = Project((pathlib.Path(__file__).parent / '..' / 'src'))
    return project.package


# TODO: part of plugin setup
def pytest_assertrepr_compare(op, left, right):
    match op, left, right:
        case 'not in', Import(), Package():
            # TODO: call helper method for nice explanation with lineno
            return [f'{left} should not be imported from {right}']
        case 'in', Import(), Package():
            return [f'{left} should be imported from {right}']
