import ast
import os
import pathlib
from typing import Sequence, Generator

from .model import Node, Import


def build_import_model(base_path: str) -> Node:
    root_node = Node(name='')
    for module_path in _walk_modules(base_path):
        with open(module_path) as module_file:
            module_ast = ast.parse(module_file.read(), module_path)
        if not module_ast.body:
            continue
        node = root_node.get_or_add(_get_node_path(base_path, module_path))
        print(_get_node_path(base_path, module_path))
        assert not node.imports
        node.imports += _collect_imports(module_ast)
    return root_node


def _get_node_path(base_path: str, module_path: str) -> Sequence[str]:
    node_path = list(pathlib.PurePath(os.path.relpath(module_path, base_path)).parts)
    if node_path[-1] == '__init__.py':
        node_path.pop()
    else:
        node_path[-1] = node_path[-1].removesuffix('.py')
    return node_path


def _collect_imports(module_ast: ast.Module) -> Sequence[Import]:
    imports: list[Import] = []
    for ast_node in module_ast.body:
        match ast_node:
            case ast.Import() as ast_import:
                for name in ast_import.names:
                    match name:
                        case ast.alias():
                            imports.append(Import(import_path=[name.name]))
                        case str():
                            imports.append(Import(import_path=[name]))
            case ast.ImportFrom() as ast_import_from:
                for name in ast_import_from.names:
                    from_path = ast_import_from.module.split('.')
                    match name:
                        case ast.alias():
                            from_path.append(name.name)
                        case str():
                            from_path.append(name)
                    imports.append(Import(import_path=from_path, level=ast_import_from.level))
    return imports


def _walk_modules(base_path: str) -> Generator[str, None, None]:
    for root, _, file_names in os.walk(base_path):
        for file_name in file_names:
            if file_name.endswith('.py'):
                yield os.path.join(root, file_name)
