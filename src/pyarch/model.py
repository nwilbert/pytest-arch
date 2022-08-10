from dataclasses import dataclass, field
from typing import Sequence, Collection, Mapping, Optional


@dataclass
class Import:
    # TODO: add lineno, turn into nested dict structure for more efficient queries?
    import_path: Sequence[str]
    level: int = 0


@dataclass
class Node:
    # TODO: add path
    name: str
    imports: Collection[Import] = field(default_factory=list)
    children: Mapping[str, 'Node'] = field(default_factory=dict)

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
