from typing import Iterable, Iterator, Optional, Tuple

from .model import DotPath, ImportInModule, ModuleNode


class FunctionLevelImport:
    def __str__(self) -> str:
        return 'function level import'

    def __repr__(self) -> str:
        # pytest uses repr for the explanation of failed assertions
        return str(self)


class ImportOf:
    """Represents a single import of something from a module."""

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
    """Represents a module tree with its imports."""

    def __init__(
        self,
        base_node: ModuleNode,
        exclude: Optional[Iterable[DotPath]] = None,
    ):
        self._base_node = base_node
        self._exclude = exclude or []

    def __contains__(self, import_: ImportOf | FunctionLevelImport) -> bool:
        """
        Checks if the given import path or any sub-path is imported anywhere
        in this package.

        Example: If the given import path is 'a.b' then an import
        of 'a.b.c' would be reported as well, but not an import of 'a'.
        """
        if isinstance(import_, ImportOf):
            return next(self._matching_imports_of(import_), None) is not None
        if isinstance(import_, FunctionLevelImport):
            return (
                next(self._matching_function_level_import(), None) is not None
            )
        raise NotImplementedError()

    def __str__(self) -> str:
        return f'modules at {self._base_node.file_path}'

    def __repr__(self) -> str:
        # pytest uses repr for the explanation of failed assertions
        return str(self)

    def explain_why_function_level_contains_is_false(self):
        return [
            f'no matching function level import in module {module_node.file_path}'
            for module_node in self._base_node.walk(exclude=self._exclude)
            if module_node.file_path.suffix == '.py'
        ]

    def explain_why_function_level_contains_is_true(self) -> list[str]:
        return [
            f'found function level import in module '
            f'{module_node.file_path}:{import_by.line_no}'
            for module_node, import_by in self._matching_function_level_import()
        ]

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
            for module_node, import_by in self._matching_imports_of(import_of)
        ]

    def _matching_function_level_import(
        self,
    ) -> Iterator[Tuple[ModuleNode, ImportInModule]]:
        for module_node in self._base_node.walk(exclude=self._exclude):
            for import_by in module_node.imports:
                if import_by.function_import:
                    yield module_node, import_by

    def _matching_imports_of(
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
