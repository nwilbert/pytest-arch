import logging
from pathlib import Path

import pytest

from pyarch.model import DotPath, ImportInModule
from pyarch.parser import build_import_model


@pytest.mark.parametrize(
    'project_structure, path, import_obj',
    [
        (
            {
                'a': {'b.py': 'from .. import y'},
            },
            'a.b',
            ImportInModule(import_path=DotPath('y'), line_no=1, level=2),
        ),
        (
            {'a': {'b': {'c.py': '...\nfrom .. import y'}}},
            'a.b.c',
            ImportInModule(import_path=DotPath('a.y'), line_no=2, level=2),
        ),
        (
            {'a': {'b.py': '...\n\nfrom .x import y'}},
            'a.b',
            ImportInModule(import_path=DotPath('a.x.y'), line_no=3, level=1),
        ),
    ],
)
def test_relative_import(project_path: Path, path: DotPath, import_obj):
    base_node = build_import_model(project_path)
    assert base_node.get(DotPath(path)).imports == [import_obj]


@pytest.mark.parametrize(
    'project_structure',
    [
        {
            'a': {'b.py': 'from ... import y'},
        }
    ],
)
def test_relative_import_beyond_base(project_path, caplog):
    base_node = build_import_model(project_path)
    warnings = [
        record
        for record in caplog.records
        if record.levelno == logging.WARNING
    ]
    assert len(warnings) == 1
    assert 'relative import' in warnings[0].msg
    assert base_node.get(DotPath('a.b')).imports == []


@pytest.mark.parametrize(
    'project_structure',
    [
        {
            'a': {'__init__.py': 'import x'},
        }
    ],
)
def test_import_from_init(project_path):
    base_node = build_import_model(project_path)
    assert base_node.get(DotPath('a')).imports == [
        ImportInModule(DotPath(('x')), 1)
    ]


@pytest.mark.parametrize(
    'project_structure, path, import_obj',
    [
        (
            {
                'a': {'b.py': 'import x'},
            },
            'a.b',
            ImportInModule(import_path=DotPath('x'), line_no=1),
        ),
        (
            {'a': {'b': {'c.py': '...\nimport x as y'}}},
            'a.b.c',
            ImportInModule(import_path=DotPath('x'), line_no=2),
        ),
    ],
)
def test_absolute_import(project_path: Path, path: DotPath, import_obj):
    base_node = build_import_model(project_path)
    assert base_node.get(DotPath(path)).imports == [import_obj]


@pytest.mark.parametrize(
    'project_structure',
    [
        {
            'a': {
                'b.py': """
                    from .x import y
                    from .x.y import z as xyz
                """,
            },
            'x': {
                '__init__.py': """
                    import a
                """,
                'y.py': """
                    import a
                    import a.b as ab
                    from a.b import c
                """,
            },
        }
    ],
)
def test_project_structure_nodes(project_path: Path):
    node = build_import_model(project_path)
    assert len(node.get(DotPath('a')).imports) == 0
    assert node.get(DotPath('a'))._file_path == project_path / 'a'
    assert len(node.get(DotPath('a.b')).imports) == 2
    assert node.get(DotPath('a.b'))._file_path == project_path / 'a' / 'b.py'
    assert len(node.get(DotPath('x')).imports) == 1
    assert (
        node.get(DotPath('x'))._file_path == project_path / 'x' / '__init__.py'
    )
    assert len(node.get(DotPath('x.y')).imports) == 3
    assert node.get(DotPath('x.y'))._file_path == project_path / 'x' / 'y.py'


@pytest.mark.parametrize(
    'project_structure',
    [
        {
            'a': {'b.py': 'import x', '.d': {'c.py': 'import x'}},
            '.m.py': 'import y',
        }
    ],
)
def test_hidden_dirs_and_files_are_excluded(project_path: Path):
    node = build_import_model(project_path)
    assert node.get(DotPath('a.b'))
    assert len(node.get(DotPath('a'))._children) == 1
    assert len(node._children) == 1
