import pytest


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': 'from b import x'}],
)
def test_arch_fixture(arch):
    assert arch.import_of('b.x') in arch.modules_at('a')
    assert arch.import_of('b.y') not in arch.modules_at('a')


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
def test_relative_import(arch):
    assert arch.import_of('x') not in arch.modules_at('a')
    assert arch.import_of('x') not in arch.modules_at('a.b')
    assert arch.import_of('a.x') in arch.modules_at('a')
    assert arch.import_of('a.x') in arch.modules_at('a.b')
    assert arch.import_of('x.y.z') not in arch.modules_at('a')
    assert arch.import_of('x.y.z') not in arch.modules_at('a.b.c')
    assert arch.import_of('a.x.y.z') in arch.modules_at('a')
    assert arch.import_of('a.x.y.z') in arch.modules_at('a.b.c')
    assert arch.import_of('x.y.m') not in arch.modules_at('a.b')


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
def test_import_absolute_argument(arch):
    assert arch.import_of('a') in arch.modules_at('a.b')
    assert arch.import_of('a.x') in arch.modules_at('a.b')
    assert arch.import_of('a.x.y') in arch.modules_at('a.b')
    assert arch.import_of('a', absolute=True) not in arch.modules_at('a.b')
    assert arch.import_of('a.x', absolute=True) not in arch.modules_at('a.b')
    assert arch.import_of('a.x.y', absolute=True) not in arch.modules_at('a.b')
    assert arch.import_of('a', absolute=False) in arch.modules_at('a.b')
    assert arch.import_of('a.x', absolute=False) in arch.modules_at('a.b')
    assert arch.import_of('a.x.y', absolute=False) in arch.modules_at('a.b')

    assert arch.import_of('x.y') in arch.modules_at('a.c')
    assert arch.import_of('x.y', absolute=False) in arch.modules_at('a.c')
    assert arch.import_of('x', absolute=False) in arch.modules_at('a.c')

    assert arch.import_of('x.y') in arch.modules_at('a.d')
    assert arch.import_of('x.y', absolute=True) in arch.modules_at('a.d')
    assert arch.import_of('x.y', absolute=False) not in arch.modules_at('a.d')


@pytest.mark.parametrize(
    'project_structure',
    [
        {
            'r': {
                'a.py': 'import x',
                'b.py': """
                    import x
                    import y
                """,
            },
        }
    ],
)
def test_modules_exclude_argument(arch):
    assert arch.import_of('y') in arch.modules_at('r')
    assert arch.import_of('y') not in arch.modules_at('r', exclude=['b'])
    assert arch.import_of('x') in arch.modules_at('r', exclude=['b'])
    assert arch.import_of('x') not in arch.modules_at('r', exclude=['a', 'b'])
    assert arch.import_of('y') not in arch.modules_at('r', exclude=['a', 'b'])


@pytest.mark.parametrize(
    'project_structure',
    [{'r': {'a.py': 'import x'}}],
)
def test_module_exclude_argument_wrong_type(arch):
    with pytest.raises(TypeError):
        arch.modules_at('r', exclude='a')
