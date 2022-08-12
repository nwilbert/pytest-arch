from pathlib import Path
from typing import Sequence

from .model import Import as ImportFromNode
from .model import Node
from .parser import build_import_model


class Import:
    """
    This means all explicit imports of elements below this.
    So a.b would also match imports of a.b.c.

    On the other hand, it does not cover imports of parent.
    So a.b would not match imports of just a.

    Note that this means that the following case can't be expressed:
        import a
        ...
        a.b()

    """

    def __init__(self, path: str):
        self._import_path = path.split('.')

    def __str__(self) -> str:
        return f'import of {".".join(self._import_path)}'

    def __repr__(self) -> str:
        # pytest uses repr for the explanation of failed assertions
        return str(self)

    @property
    def import_path(self) -> Sequence[str]:
        return self._import_path


class Package:
    def __init__(self, base_node: Node, path: str):
        self._base_node = base_node
        self._relative_path = path

    def __contains__(self, import_of: Import) -> bool:
        assert isinstance(import_of, Import)
        import_of_path = import_of.import_path
        matching_imports: list[ImportFromNode] = []

        # TODO: add support for level / relative import
        #  (add node base path if level > 0)
        # NOTE: could use set of tuples (with all truncations),
        # for more efficient initial querying.
        def add_matching_imports(node: Node) -> None:
            for import_by in node.imports:
                import_by_path = import_by.import_path
                if len(import_of_path) > len(import_by_path):
                    continue
                if import_of_path == import_by_path[: len(import_of_path)]:
                    matching_imports.append(import_by)

        self._base_node.walk(add_matching_imports)
        return len(import_of_path) > 0

    def __str__(self) -> str:
        return f'package {self._relative_path}'

    def __repr__(self) -> str:
        # pytest uses repr for the explanation of failed assertions
        return str(self)


class Project:
    def __init__(self, path: Path):
        self._base_path = path.resolve(strict=True)
        self._base_node = build_import_model(self._base_path)

    def package(self, path: str) -> Package:
        return Package(self._base_node.get(path.split('.')), path)
