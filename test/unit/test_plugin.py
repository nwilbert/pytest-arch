import pytest

from pyarch import must_import, must_not_import, must_not_import_private, project, scope


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': 'from b import x'}],
)
def test_check_must_import_passes(arch):
    arch.check({'a': must_import('b.x')})


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': 'from b import x'}],
)
def test_check_must_import_fails(arch):
    with pytest.raises(AssertionError, match='must import'):
        arch.check({'a': must_import('c')})


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': 'from b import x'}],
)
def test_check_must_not_import_passes(arch):
    arch.check({'a': must_not_import('c')})


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': 'from b import x'}],
)
def test_check_must_not_import_fails(arch):
    with pytest.raises(AssertionError, match='must not import'):
        arch.check({'a': must_not_import('b')})


@pytest.mark.parametrize(
    'project_structure',
    [{'r': {'a.py': 'import x', 'b.py': 'import y'}}],
)
def test_check_scope_without(arch):
    arch.check({scope('r', without='b'): must_not_import('y')})
    with pytest.raises(AssertionError):
        arch.check({scope('r', without='b'): must_not_import('x')})


@pytest.mark.parametrize(
    'project_structure',
    [{'r': {'a.py': 'import x', 'b.py': 'import y'}}],
)
def test_check_collects_all_failures(arch):
    with pytest.raises(AssertionError) as exc_info:
        arch.check({'r': [must_not_import('x'), must_not_import('y')]})
    msg = str(exc_info.value)
    assert 'a.py' in msg
    assert 'b.py' in msg


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': 'from b import x'}],
)
def test_check_list_of_predicates(arch):
    arch.check({'a': [must_import('b'), must_not_import('c')]})


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': ''}],
)
def test_check_module_not_found(arch):
    with pytest.raises(KeyError):
        arch.check({'foobar': must_not_import('x')})


@pytest.mark.parametrize(
    'project_structure',
    [
        {
            'a': {
                'b.py': 'from .x import y',
                'd.py': 'from x import y',
            }
        }
    ],
)
def test_check_via(arch):
    arch.check({'a.b': must_not_import('a.x', via='absolute')})
    arch.check({'a.d': must_not_import('x', via='relative')})
    with pytest.raises(AssertionError):
        arch.check({'a.b': must_not_import('a.x', via='relative')})


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': 'from b import x'}],
)
def test_check_must_not_import_private_passes(arch):
    arch.check({'a': must_not_import_private()})


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': 'from b import _x'}],
)
def test_check_must_not_import_private_fails(arch):
    with pytest.raises(AssertionError, match='must not import private'):
        arch.check({'a': must_not_import_private()})


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': 'from b import _x\nfrom c import _y'}],
)
def test_check_must_not_import_private_with_path(arch):
    arch.check({'a': must_not_import_private('c2')})
    with pytest.raises(AssertionError):
        arch.check({'a': must_not_import_private('b')})


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': 'from b import _x', 'c.py': 'from e import y'}],
)
def test_check_project_scope(arch):
    arch.check({project(): must_not_import('d')})
    with pytest.raises(AssertionError):
        arch.check({project(): must_not_import_private()})
