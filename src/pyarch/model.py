from dataclasses import dataclass
from pathlib import PurePath
from typing import Any, Callable, Iterable, Optional, Sequence, Union


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
class ImportInModule:
    # TODO: add lineno
    import_path: DotPath
    level: int = 0


class RootNode:
    def __init__(self) -> None:
        self._children: dict[str, 'ModuleNode'] = {}

    def get(self, path: DotPath) -> Optional['ModuleNode']:
        if not path.parts:
            raise KeyError('Empty path is not supported on root node.')
        if child := self._children.get(path.parts[0]):
            remaining_path = (
                DotPath(path.parts[1:]) if len(path.parts) > 1 else DotPath()
            )
            return child.get(remaining_path)
        return None

    def get_or_add(self, path: DotPath) -> 'ModuleNode':
        if not path.parts:
            raise KeyError('Empty path is not supported on root node.')
        name = path.parts[0]
        remaining_path = (
            DotPath(path.parts[1:]) if len(path.parts) > 1 else DotPath()
        )
        if not (child := self._children.get(name)):
            child = ModuleNode(name=name)
            self._children[name] = child
        return child.get_or_add(remaining_path)


@dataclass
class ModuleNode(RootNode):
    # TODO: add full path on disk and relative path with respect
    #  to project root

    def __init__(self, name: str):
        super().__init__()
        self._name: str = name
        self._imports: list[ImportInModule] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def imports(self) -> Sequence[ImportInModule]:
        return self._imports

    def add_import(self, *imports: ImportInModule) -> None:
        self._imports += imports

    def get(self, path: DotPath) -> Optional['ModuleNode']:
        if not path.parts:
            return self
        return super().get(path)

    def get_or_add(self, path: DotPath) -> 'ModuleNode':
        if not path.parts:
            return self
        return super().get_or_add(path)

    def walk(self, func: Callable[['ModuleNode'], None]) -> None:
        func(self)
        for child in self._children.values():
            child.walk(func)
