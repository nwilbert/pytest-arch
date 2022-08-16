from dataclasses import dataclass, field
from pathlib import PurePath
from typing import Any, Callable, Iterable, Optional, Union


class DotPath:
    """
    Represent a 'path' with dot as the separator,
    as it is used in Python imports.

    Largely follows the Path interface from pathlib.
    """
    def __init__(self, path: str | Iterable[str] | 'DotPath' | None = None):
        self._parts: tuple[str, ...]
        if not path:
            self._parts = tuple()
        elif isinstance(path, str):
            self._parts = tuple(path.split('.'))
        elif isinstance(path, DotPath):
            self._parts = path.parts
        else:
            self._parts = tuple(path)

    @classmethod
    def from_path(cls, path: PurePath) -> 'DotPath':
        parts = list(path.parts)
        if len(parts) == 0:
            return DotPath()
        if parts[-1] == '__init__.py':
            parts.pop()
        else:
            parts[-1] = parts[-1].removesuffix('.py')
        return cls(parts)

    def is_relative_to(self, other: 'DotPath') -> bool:
        if len(other.parts) > len(self.parts):
            return False
        if other.parts == self.parts[: len(other.parts)]:
            return True
        return False

    @property
    def parts(self) -> tuple[str, ...]:
        return self._parts

    @property
    def name(self) -> str:
        return self._parts[-1]

    @property
    def parent(self) -> 'DotPath':
        return DotPath(self._parts[:-1])

    def __str__(self) -> str:
        return '.'.join(self._parts)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.parts})'

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, DotPath):
            return NotImplemented
        return self._parts == other._parts

    def __truediv__(self, other: Union['DotPath', str]) -> 'DotPath':
        return DotPath(self.parts + DotPath(other).parts)

    def __rtruediv__(self, other: Union['DotPath', str]) -> 'DotPath':
        return DotPath(DotPath(other).parts + self.parts)


@dataclass
class Import:
    # TODO: add lineno, turn into nested dict structure
    #  for more efficient queries?
    import_path: DotPath
    level: int = 0


@dataclass
class Node:
    # TODO: add full path on disk and relative path with respect
    #  to project root
    # TODO: do not inherit from dataclass
    name: str
    imports: list[Import] = field(default_factory=list)
    children: dict[str, 'Node'] = field(default_factory=dict)

    def get(self, path: DotPath) -> Optional['Node']:
        if not path.parts:
            return self
        if child := self.children.get(path.parts[0]):
            remaining_path = (
                DotPath(path.parts[1:]) if len(path.parts) > 1 else DotPath()
            )
            return child.get(remaining_path)
        return None

    def get_or_add(self, path: DotPath) -> 'Node':
        if not path.parts:
            return self
        name = path.parts[0]
        remaining_path = (
            DotPath(path.parts[1:]) if len(path.parts) > 1 else DotPath()
        )
        if not (child := self.children.get(name)):
            child = Node(name=name)
            self.children[name] = child
        return child.get_or_add(remaining_path)

    def walk(self, func: Callable[['Node'], None]) -> None:
        func(self)
        if not self.children:
            return
        for child in self.children.values():
            child.walk(func)
