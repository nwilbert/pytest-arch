from .model import DotPath, ModuleNode


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

    def __init__(self, path: DotPath):
        self._import_path = path

    def __str__(self) -> str:
        return f'import of {self._import_path}'

    def __repr__(self) -> str:
        # pytest uses repr for the explanation of failed assertions
        return str(self)

    @property
    def import_path(self) -> DotPath:
        return self._import_path

    @classmethod
    def from_str_path(cls, dot_path: str) -> 'ImportOf':
        return cls(DotPath(dot_path))


class ModulesAt:
    """
    Represents a module with its imports.

    Via the contains magic method you can check if it
    does or does not contain certain imports.
    """

    def __init__(self, base_node: ModuleNode):
        self._base_node = base_node

    def __contains__(self, import_of: ImportOf) -> bool:
        """
        Checks if the given import path or any sub-path is imported anywhere
        in this package.

        Example: If the given import path is 'a.b' then an import
        of 'a.b.c' would be reported as well, but not an import of 'a'.
        """
        import_of_path = import_of.import_path
        for module_node in self._base_node.walk():
            for import_by in module_node.imports:
                if import_by.import_path.is_relative_to(import_of_path):
                    return True
        return False

    def explain_contains_false(self, import_of: ImportOf) -> list[str]:
        assert import_of not in self
        return [
            f'no matching import in module {module_node.file_path}'
            for module_node in self._base_node.walk()
            if module_node.file_path.suffix == '.py'
        ]

    def explain_not_contains_false(self, import_of: ImportOf) -> list[str]:
        import_of_path = import_of.import_path
        explanations: list[str] = []
        for module_node in self._base_node.walk():
            for import_by in module_node.imports:
                if import_by.import_path.is_relative_to(import_of_path):
                    explanations.append(
                        f'found import of {import_of.import_path} in module '
                        f'{module_node.file_path}:{import_by.line_no}'
                    )
        assert explanations
        return explanations

    def __str__(self) -> str:
        return f'modules at {self._base_node.file_path}'

    def __repr__(self) -> str:
        # pytest uses repr for the explanation of failed assertions
        return str(self)

    # TODO: implement "except" (return new instance of ModulesAt)
    #  e.g. modules_at('bobbytime.models').except('repository')
