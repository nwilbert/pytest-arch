import logging
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

import pytest

from .assertion import ImportOf, ModulesAt
from .model import DotPath, RootNode
from .parser import build_import_model

log = logging.getLogger(__name__)

INI_NAME = 'arch_project_paths'
PROJECT_CONFIG_FILES = ['pyproject.toml', 'setup.cfg', 'setup.py']


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
    """
    Provides the project source code paths that are analyzed.

    This fixture normally isn't used explicitly in tests, unless you want
    to check that the project paths are set correctly.

    Logic for finding the project path:
     1. If there is an `arch_project_paths` config entry in the pytest config
        then use that and be done.
     2. If there is no config then start with the pytest root path.
     3. Go up until a `pyproject.toml`, `setup.cfg`, or `setup.py` is found.
     4. If there is a `src` directory directly below then use that,
        otherwise use the path from step 3.
    """
    # Note: pytest already converts relative to absolute paths.
    if project_paths := pytestconfig.getini(INI_NAME):
        return project_paths  # type: ignore[no-any-return]
    # Note: pytest considers config files in its rootpath heuristic
    #   only if those files actually contain pytest config.
    for path in (pytestconfig.rootpath, *pytestconfig.rootpath.parents):
        for config_file in PROJECT_CONFIG_FILES:
            if (path / config_file).exists():
                if (src_path := path / 'src').exists():
                    return [src_path]
                return [path]
    return [pytestconfig.rootpath]


@pytest.fixture
def arch_root_node(arch_project_paths: Sequence[Path]) -> RootNode:
    """
    Provides the root node of the tree of analyzed Python modules.

    Normally this isn't used explicitly in tests.
    """
    if len(arch_project_paths) != 1:
        raise NotImplementedError()
    log.info(f'creating architecture model for {arch_project_paths[0]}')
    return build_import_model(arch_project_paths[0])


class ArchFixture:
    """Factory for architecture objects to be used in test assertions."""

    def __init__(self, arch_root_node: RootNode):
        self._root_node = arch_root_node

    def modules_at(
        self, path: str, *, exclude: Optional[Iterable[str]] = None
    ) -> ModulesAt:
        node = self._root_node.get(DotPath(path))
        if not node:
            raise KeyError(f'Found no node for path {path} in project.')
        if isinstance(exclude, str):
            raise TypeError(
                f'Value "{exclude}" for exclude argument is of type str, '
                f'but should be an iterable (like ["{exclude}"]).'
            )
        return ModulesAt(node, exclude=[DotPath(e) for e in exclude or []])

    @staticmethod
    def import_of(dot_path: str, *, absolute: bool | None = None) -> ImportOf:
        return ImportOf(DotPath(dot_path), absolute=absolute)


@pytest.fixture
def arch(arch_root_node: RootNode) -> ArchFixture:
    """
    Provides a factory that is used to create the architecture representation
    objects for test assertions.
    """
    return ArchFixture(arch_root_node)
