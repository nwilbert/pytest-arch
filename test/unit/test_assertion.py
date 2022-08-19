import pytest


@pytest.mark.parametrize(
    'project_structure',
    [
        {
            'a.py': """
                from b import x
            """,
            'b.py': """
                import a
            """,
        }
    ],
)
def test_absolute_import_assertion(package, import_of):
    assert import_of('a') in package('b')
    assert import_of('c') not in package('b')
    assert import_of('b.x') in package('a')
    assert import_of('b.y') not in package('a')


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
def test_relative_import_assertion(package, import_of):
    assert import_of('x') not in package('a')
    assert import_of('a.x') in package('a')
    assert import_of('x') not in package('a.b')
    assert import_of('a.x') in package('a.b')
    # assert import_of('x.y.z') in package('a')
    # assert import_of('x.y.z') in package('a.b')
    # assert import_of('x.y.m') not in package('a')
    # assert import_of('x.y.m') not in package('a.b')
