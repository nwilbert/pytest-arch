import logging
from pathlib import Path

import pytest

from pyarch.model import DotPath, Import
from pyarch.parser import build_import_model


@pytest.mark.parametrize(
    'project_structure, path, import_obj',
    [
        (
            {
                'a': {'b.py': 'from .. import y'},
            },
            'a.b',
            Import(import_path=DotPath('y'), level=2),
        ),
        (
            {'a': {'b': {'c.py': 'from .. import y'}}},
            'a.b.c',
            Import(import_path=DotPath('a.y'), level=2),
        ),
        (
            {'a': {'b.py': 'from .x import y'}},
            'a.b',
            Import(import_path=DotPath('a.x.y'), level=1),
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
            'a': {
                '__init__.py': '',
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
    assert set(node.children.keys()) == {'a', 'x'}
    assert set(node.children['a'].children.keys()) == {'b'}
    assert set(node.children['x'].children.keys()) == {'y'}

    assert len(node.get(DotPath('a')).imports) == 0
    assert len(node.get(DotPath('a.b')).imports) == 2
    assert len(node.get(DotPath('x')).imports) == 1
    assert len(node.get(DotPath('x.y')).imports) == 3
