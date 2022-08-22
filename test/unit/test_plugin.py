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
