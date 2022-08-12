from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence

# TODO: do not inherit from dataclass
# TODO: add new type ImportPath that works similar to PosixPath but with dots (could then replace the Imort classs from testhelpers)


@dataclass
class Import:
    # TODO: add lineno, turn into nested dict structure for more efficient queries?
    import_path: Sequence[str]
    level: int = 0


@dataclass
class Node:
    # TODO: add full path on disk and relative path with respect to project root
    name: str
    imports: list[Import] = field(default_factory=list)
    children: dict[str, 'Node'] = field(default_factory=dict)

    def get(self, path: Sequence[str]) -> Optional['Node']:
        if path:
            name, remaining_path = path[0], path[1:]
            child = self.children.get(name)
            if child:
                return child.get(remaining_path)
            else:
                return None
        else:
            return self

    def get_or_add(self, path: Sequence[str]) -> 'Node':
        if path:
            name, remaining_path = path[0], path[1:]
            if not (child := self.children.get(name)):
                child = Node(name=name)
                self.children[name] = child
            return child.get_or_add(remaining_path)
        else:
            return self

    def walk(self, func: Callable[['Node'], None]):
        func(self)
        for child in self.children.values():
            child.walk(func)
