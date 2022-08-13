import pathlib
from inspect import cleandoc

import pytest

pytest_plugins = 'pytester'


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
def project_path(project_structure, tmp_path):
    _create_project_structure(project_structure, pathlib.Path(tmp_path))
    return tmp_path
