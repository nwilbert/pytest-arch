import pytest


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': 'from b import x'}],
)
def test_fixtures(modules_at, import_of):
    assert import_of('b.x') in modules_at('a')
    assert import_of('b.y') not in modules_at('a')


@pytest.mark.parametrize(
    'project_structure',
    [
        {
            'a': {
                'b': {
                    'c.py': """
                        from .. import x
                        from ..x.y import z as xyz
                    """,
                }
            },
        }
    ],
)
def test_relative_import_assertion(modules_at, import_of):
    assert import_of('x') not in modules_at('a')
    assert import_of('x') not in modules_at('a.b')
    assert import_of('a.x') in modules_at('a')
    assert import_of('a.x') in modules_at('a.b')
    assert import_of('x.y.z') not in modules_at('a')
    assert import_of('x.y.z') not in modules_at('a.b.c')
    assert import_of('a.x.y.z') in modules_at('a')
    assert import_of('a.x.y.z') in modules_at('a.b.c')
    assert import_of('x.y.m') not in modules_at('a.b')


@pytest.mark.parametrize(
    'project_structure',
    [
        {
            'a': {
                'b.py': 'from .x import y',
                'c.py': 'from ..x import y',
                'd.py': 'from x import y',
            },
        }
    ],
)
def test_absolute_import_flag(modules_at, import_of):
    assert import_of('a') in modules_at('a.b')
    assert import_of('a.x') in modules_at('a.b')
    assert import_of('a.x.y') in modules_at('a.b')
    assert import_of('a', absolute=True) not in modules_at('a.b')
    assert import_of('a.x', absolute=True) not in modules_at('a.b')
    assert import_of('a.x.y', absolute=True) not in modules_at('a.b')
    assert import_of('a', absolute=False) in modules_at('a.b')
    assert import_of('a.x', absolute=False) in modules_at('a.b')
    assert import_of('a.x.y', absolute=False) in modules_at('a.b')

    assert import_of('x.y') in modules_at('a.c')
    assert import_of('x.y', absolute=False) in modules_at('a.c')
    assert import_of('x', absolute=False) in modules_at('a.c')

    assert import_of('x.y') in modules_at('a.d')
    assert import_of('x.y', absolute=True) in modules_at('a.d')
    assert import_of('x.y', absolute=False) not in modules_at('a.d')
