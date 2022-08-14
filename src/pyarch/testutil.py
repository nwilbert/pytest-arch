from .model import DotPath
from .model import Import as ImportFromNode
from .model import Node


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
        self._import_path = DotPath(path)

    def __str__(self) -> str:
        return f'import of {self._import_path}'

    def __repr__(self) -> str:
        # pytest uses repr for the explanation of failed assertions
        return str(self)

    @property
    def import_path(self) -> DotPath:
        return self._import_path


class Package:
    def __init__(self, base_node: Node):
        self._base_node = base_node

    def __contains__(self, import_of: Import) -> bool:
        """
        Checks if the given import path or any sub-path is imported anywhere
        in this package.

        Example: If the given import path is 'a.b' then an import
        of 'a.b.c' would be reported as well, but not an import of 'a'.
        """
        assert isinstance(import_of, Import)
        import_of_path = import_of.import_path
        matching_imports: list[ImportFromNode] = []

        def add_matching_imports(node: Node) -> None:
            for import_by in node.imports:
                import_by_path = import_by.import_path
                if import_by_path.startswith(import_of_path):
                    matching_imports.append(import_by)

        self._base_node.walk(add_matching_imports)
        return len(matching_imports) > 0

    def __str__(self) -> str:
        return f'package {self._base_node}'

    def __repr__(self) -> str:
        # pytest uses repr for the explanation of failed assertions
        return str(self)
