from __future__ import annotations

import logging
from collections.abc import Sequence
from pathlib import Path

import pytest

from .model import RootNode
from .parser import build_import_model
from .query import Predicate, Scope, evaluate_rules

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


@pytest.fixture(scope='session')
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


@pytest.fixture(scope='session')
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
    """Provides architecture rule checking for test assertions."""

    def __init__(self, arch_root_node: RootNode):
        self._root_node = arch_root_node

    def check(self, rules: dict[str | Scope, Predicate | list[Predicate]]) -> None:
        """
        Check a set of architecture import rules.

        Raises AssertionError listing all violations if any rules fail.
        """
        failures = evaluate_rules(self._root_node, rules)
        if failures:
            raise AssertionError(
                'Architecture rule violations:\n' + '\n'.join(failures)
            )


@pytest.fixture
def arch(arch_root_node: RootNode) -> ArchFixture:
    """
    Provides a factory that is used to create the architecture representation
    objects for test assertions.
    """
    return ArchFixture(arch_root_node)
