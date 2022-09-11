import logging
from pathlib import Path
from typing import Any, Callable, Iterable, Optional, Sequence

import pytest

from .assertion import ImportOf, ModulesAt
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
    op: str, left: Any, right: Any
) -> Sequence[str] | None:
    match op, left, right:
        case 'not in', ImportOf() as import_of, ModulesAt() as package:
            first_line = f'{left} {op} {right}'
            return [first_line] + package.explain_not_contains_false(import_of)
        case 'in', ImportOf() as import_of, ModulesAt() as package:
            first_line = f'{left} {op} {right}'
            return [first_line] + package.explain_contains_false(import_of)
    return None


@pytest.fixture
def arch_project_paths(pytestconfig: pytest.Config) -> Sequence[Path]:
    # Note: pytest already converts relative to absolute paths
    paths = pytestconfig.getini(INI_NAME)
    if not paths:
        # TODO: raise error, to avoid confusion?
        # Note: rootpath is only picked correctly
        #   if pytest finds actual config for pytest.
        paths = [pytestconfig.rootpath]
    return paths  # type: ignore[no-any-return]


@pytest.fixture
def arch_root_node(arch_project_paths: Sequence[Path]) -> RootNode:
    if len(arch_project_paths) != 1:
        raise NotImplementedError()
    log.info(f'creating architecture model for {arch_project_paths[0]}')
    return build_import_model(arch_project_paths[0])


@pytest.fixture
def modules_at(arch_root_node: RootNode) -> Callable[[str], ModulesAt]:
    def _create_modules_at(
        path: str, *, exclude: Optional[Iterable[str]] = None
    ) -> ModulesAt:
        node = arch_root_node.get(DotPath(path))
        if not node:
            raise KeyError(f'Found no node for path {path} in project.')
        if isinstance(exclude, str):
            raise TypeError(
                f'Value "{exclude}" for exclude argument is of type str, '
                f'but should be an iterable (like ["{exclude}"]).'
            )
        return ModulesAt(node, exclude=[DotPath(e) for e in exclude or []])

    return _create_modules_at


@pytest.fixture
def import_of() -> Callable[[str], ImportOf]:
    return ImportOf.from_str_path
