import ast
import logging
from pathlib import Path
from typing import Generator, Sequence, Tuple

from .model import DotPath, Import, Node

log = logging.getLogger(__name__)


def build_import_model(base_path: Path) -> Node:
    root_node = Node(name='')
    for module_path, module_content in _walk_modules(base_path):
        module_ast = ast.parse(module_content, str(module_path))
        if not module_ast.body:
            continue
        dot_path = DotPath.from_path(module_path.relative_to(base_path))
        node = root_node.get_or_add(dot_path)
        assert not node.imports
        node.imports += _collect_imports(module_ast, dot_path)
    return root_node


def _collect_imports(
    module_ast: ast.Module, node_path: DotPath
) -> Sequence[Import]:
    imports: list[Import] = []
    for ast_node in module_ast.body:
        match ast_node:
            case ast.Import() as ast_import:
                for name in ast_import.names:
                    match name:
                        case ast.alias():
                            imports.append(Import(DotPath(name.name)))
                        case str():
                            imports.append(Import(DotPath(name)))
            case ast.ImportFrom() as ast_import_from:
                for name in ast_import_from.names:
                    if ast_import_from.module:
                        from_path = DotPath(ast_import_from.module)
                    else:
                        from_path = DotPath()
                    if (level := ast_import_from.level) > 0:
                        if level > len(node_path.parts):
                            log.warning(
                                f'Skipping import from {node_path} because '
                                f'relative import level goes beyond project.'
                            )
                            continue
                        else:
                            from_path = (
                                DotPath(node_path.parts[:-level]) / from_path
                            )
                    match name:
                        case ast.alias():
                            from_path /= name.name
                        case str():
                            from_path /= name
                    imports.append(
                        Import(
                            import_path=from_path, level=ast_import_from.level
                        )
                    )
    return imports


def _walk_modules(base_path: Path) -> Generator[Tuple[Path, str], None, None]:
    for path in base_path.glob('**/*.py'):
        if not any(part.startswith('.') for part in path.parts):
            yield path, path.read_text()
