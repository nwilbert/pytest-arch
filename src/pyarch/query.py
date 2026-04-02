from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Literal

from .model import DotPath, ImportInModule, ModuleNode


@dataclass(frozen=True)
class Scope:
    """A module scope (package or module) to be checked for imports."""

    path: str
    without: tuple[str, ...] = ()


def scope(path: str, *, without: str | list[str] | None = None) -> Scope:
    if isinstance(without, str):
        without = [without]
    return Scope(path=path, without=tuple(without or []))


@dataclass(frozen=True)
class CanImport:
    """Predicate asserting that a scope must contain a given import."""

    path: str
    via: Literal['absolute', 'relative'] | None = None


def can_import(
    path: str, *, via: Literal['absolute', 'relative'] | None = None
) -> CanImport:
    return CanImport(path=path, via=via)


@dataclass(frozen=True)
class MustNotImport:
    """Predicate asserting that a scope must not contain a given import."""

    path: str
    via: Literal['absolute', 'relative'] | None = None


def must_not_import(
    path: str, *, via: Literal['absolute', 'relative'] | None = None
) -> MustNotImport:
    return MustNotImport(path=path, via=via)


def _find_matching_imports(
    base_node: ModuleNode,
    exclude: list[DotPath],
    import_path: DotPath,
    via: Literal['absolute', 'relative'] | None,
) -> Iterator[tuple[ModuleNode, ImportInModule]]:
    absolute = _via_to_absolute(via)
    for module_node in base_node.walk(exclude=exclude):
        for import_by in module_node.imports:
            if import_by.import_path.is_relative_to(import_path):
                if absolute is None or absolute != bool(import_by.level):
                    yield module_node, import_by


def _via_to_absolute(via: Literal['absolute', 'relative'] | None) -> bool | None:
    if via == 'absolute':
        return True
    if via == 'relative':
        return False
    return None
