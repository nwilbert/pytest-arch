import pathlib
from typing import Callable, Sequence

import pytest

from pyarch.testutil import Import, Package, Project


@pytest.fixture
def project(project_path: pathlib.Path) -> Project:
    # TODO: by default go up until there is an 'src' dir,
    #  or a pyproject.toml and read from it
    return Project(project_path)


@pytest.fixture
def package(project: Project) -> Callable[[str], Package]:
    return project.package


# TODO: part of plugin setup
def pytest_assertrepr_compare(
    op: str, left: str, right: str
) -> Sequence[str] | None:
    match op, left, right:
        case 'not in', Import(), Package():
            # TODO: call helper method for nice explanation with lineno
            return [f'{left} should not be imported from {right}']
        case 'in', Import(), Package():
            return [f'{left} should be imported from {right}']
    return None
