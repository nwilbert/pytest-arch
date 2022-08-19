import logging
from pathlib import Path
from typing import Callable, Sequence

import pytest

from .assertion import ImportOf, Package
from .model import DotPath, RootNode
from .parser import build_import_model

INI_NAME = 'arch_project_paths'

log = logging.getLogger(__name__)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addini(
        INI_NAME,
        type='paths',
        help='Paths for pytest-arch source code analysis '
        '(relative to rootpath or absolute).',
    )


def pytest_assertrepr_compare(
    op: str, left: str, right: str
) -> Sequence[str] | None:
    match op, left, right:
        case 'not in', ImportOf(), Package():
            # TODO: call helper method for nice explanation with lineno
            return [f'{left} should not be imported from {right}']
        case 'in', ImportOf(), Package():
            return [f'{left} should be imported from {right}']
    return None


@pytest.fixture
def arch_project_paths(pytestconfig: pytest.Config) -> Sequence[Path]:
    # note that pytest already converts relative to absolute paths
    paths = pytestconfig.getini(INI_NAME)
    if not paths:
        paths = [pytestconfig.rootpath]
    return paths  # type: ignore[no-any-return]


@pytest.fixture
def arch_root_node(arch_project_paths: Sequence[Path]) -> RootNode:
    if len(arch_project_paths) != 1:
        raise NotImplementedError()
    log.info(f'creating architecture model for {arch_project_paths[0]}')
    return build_import_model(arch_project_paths[0])


@pytest.fixture
def package(arch_root_node: RootNode) -> Callable[[str], Package]:
    def _create_package(path: str) -> Package:
        node = arch_root_node.get(DotPath(path))
        if not node:
            raise KeyError(f'Found no node for path {path} in project.')
        return Package(node)

    return _create_package


@pytest.fixture
def import_of() -> Callable[[str], ImportOf]:
    return ImportOf.from_str_path


# TODO: implement "without"
# assert import_of('a.b') not in
# package('bobbytime.models').without('repository')
# TODO: implment import variations
# assert Import_of_exactly('bobbytime.database')
# not in package('bobbytime.models').without('repository')
