import ast
import logging
from pathlib import Path
from typing import Generator, Sequence, Tuple

from .model import DotPath, ImportInModule, RootNode

log = logging.getLogger(__name__)


def build_import_model(base_path: Path) -> RootNode:
    root_node = RootNode()
    for module_path, module_content in _walk_modules(base_path):
        module_ast = ast.parse(module_content, str(module_path))
        dot_path = DotPath.from_path(module_path.relative_to(base_path))
        node = root_node.get_or_add(dot_path, module_path)
        imports = _collect_imports(module_ast, dot_path)
        if module_path.name == '__init__.py':
            node.add_data_for_init_file(imports)
        else:
            node.add_imports(imports)
    return root_node


def _collect_imports(
    module_ast: ast.AST, node_path: DotPath, *, in_function: bool = False
) -> Sequence[ImportInModule]:
    imports: list[ImportInModule] = []
    for ast_node in ast.iter_child_nodes(module_ast):
        match ast_node:
            case ast.Import() as ast_import:
                imports.extend(
                    _convert_import(ast_import, function_import=in_function)
                )
            case ast.ImportFrom() as ast_import_from:
                imports.extend(
                    _convert_import_from(
                        ast_import_from, node_path, function_import=in_function
                    )
                )
            case ast.FunctionDef() as ast_function_def:
                imports.extend(
                    _collect_imports(
                        ast_function_def, node_path, in_function=True
                    )
                )
            case _:
                imports.extend(_collect_imports(ast_node, node_path))
    return imports


def _convert_import(
    ast_import: ast.Import, *, function_import: bool = False
) -> Sequence[ImportInModule]:
    imports = []
    for alias in ast_import.names:
        imports.append(
            ImportInModule(
                import_path=DotPath(alias.name),
                line_no=alias.lineno,
                function_import=function_import,
            )
        )
    return imports


def _convert_import_from(
    ast_import_from: ast.ImportFrom,
    node_path: DotPath,
    *,
    function_import: bool = False,
) -> Sequence[ImportInModule]:
    imports = []
    for alias in ast_import_from.names:
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
                from_path = DotPath(node_path.parts[:-level]) / from_path
        from_path /= alias.name
        imports.append(
            ImportInModule(
                import_path=from_path,
                line_no=alias.lineno,
                level=ast_import_from.level,
                function_import=function_import,
            )
        )
    return imports


def _walk_modules(base_path: Path) -> Generator[Tuple[Path, str], None, None]:
    for path in base_path.glob('**/*.py'):
        if not any(part.startswith('.') for part in path.parts):
            yield path, path.read_text()
