from typing import Iterable, Iterator, Optional, Tuple

from .model import DotPath, ImportInModule, ModuleNode


class ImportOf:
    """
    Represents a single import of something from a module.

    This includes imports of child elements.
    So a.b would also match imports of a.b.c.

    On the other hand, it does not cover imports of parent.
    So a.b would not match imports of a.

    Note that this means that the following case can't be expressed:
        import a
        ...
        a.b()

    """

    def __init__(self, path: DotPath, *, absolute: bool | None = None):
        self._import_path = path
        self._absolute = absolute

    def __str__(self) -> str:
        return f'import of {self._import_path}'

    def __repr__(self) -> str:
        # pytest uses repr for the explanation of failed assertions
        return str(self)

    @property
    def import_path(self) -> DotPath:
        return self._import_path

    @property
    def absolute(self) -> bool | None:
        return self._absolute


class ModulesAt:
    """
    Represents a module with its imports.

    Via the contains magic method you can check if it
    does or does not contain certain imports.
    """

    def __init__(
        self,
        base_node: ModuleNode,
        exclude: Optional[Iterable[DotPath]] = None,
    ):
        self._base_node = base_node
        self._exclude = exclude or []

    def __contains__(self, import_of: ImportOf) -> bool:
        """
        Checks if the given import path or any sub-path is imported anywhere
        in this package.

        Example: If the given import path is 'a.b' then an import
        of 'a.b.c' would be reported as well, but not an import of 'a'.
        """
        return next(self._matching_imports(import_of), None) is not None

    def __str__(self) -> str:
        return f'modules at {self._base_node.file_path}'

    def __repr__(self) -> str:
        # pytest uses repr for the explanation of failed assertions
        return str(self)

    def explain_why_contains_is_false(self, import_of: ImportOf) -> list[str]:
        return [
            f'no matching import in module {module_node.file_path}'
            for module_node in self._base_node.walk(exclude=self._exclude)
            if module_node.file_path.suffix == '.py'
        ]

    def explain_why_contains_is_true(self, import_of: ImportOf) -> list[str]:
        return [
            f'found import of {import_of.import_path} in module '
            f'{module_node.file_path}:{import_by.line_no}'
            for module_node, import_by in self._matching_imports(import_of)
        ]

    def _matching_imports(
        self, import_of: ImportOf
    ) -> Iterator[Tuple[ModuleNode, ImportInModule]]:
        import_of_path = import_of.import_path
        for module_node in self._base_node.walk(exclude=self._exclude):
            for import_by in module_node.imports:
                if import_by.import_path.is_relative_to(import_of_path):
                    if (
                        import_of.absolute is None
                        or import_of.absolute != bool(import_by.level)
                    ):
                        yield module_node, import_by
