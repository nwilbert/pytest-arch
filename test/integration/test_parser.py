import pytest

from pyarch.parser import build_import_model


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
def test_project_on_disk(project_path):
    node = build_import_model(project_path)
    assert set(node.children.keys()) == {'a', 'x'}
    assert set(node.children['a'].children.keys()) == {'b'}
    assert set(node.children['x'].children.keys()) == {'y'}

    assert len(node.get(['a']).imports) == 0
    assert len(node.get(['a', 'b']).imports) == 2
    assert len(node.get(['x']).imports) == 1
    assert len(node.get(['x', 'y']).imports) == 3
