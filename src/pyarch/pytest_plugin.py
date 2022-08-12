import pathlib

import pytest

from pyarch.testutil import Import, Package, Project


@pytest.fixture
def package():
    # TODO: by default go up until there is an 'src' dir, or a pyproject.toml and read from it
    project = Project((pathlib.Path(__file__).parent.parent))
    return project.package


# TODO: part of plugin setup
def pytest_assertrepr_compare(op, left, right):
    match op, left, right:
        case 'not in', Import(), Package():
            # TODO: call helper method for nice explanation with lineno
            return [f'{left} should not be imported from {right}']
        case 'in', Import(), Package():
            return [f'{left} should be imported from {right}']
