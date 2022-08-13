import pytest

from pyarch.testutil import Import as import_of


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
def test_absolute_import_assertion(package):
    assert import_of('a') in package('b')
    assert import_of('c') not in package('b')
    assert import_of('b.x') in package('a')
    assert import_of('b.y') not in package('a')


# TODO: implement "without"
# assert import_of('a.b') not in
# package('bobbytime.models').without('repository')
# TODO: implment import variations
# assert Import_of_exactly('bobbytime.database')
# not in package('bobbytime.models').without('repository')
