import pytest

from pyarch import can_import, must_not_import, scope


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': 'from b import x'}],
)
def test_check_can_import_passes(arch):
    arch.check({'a': can_import('b.x')})


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': 'from b import x'}],
)
def test_check_can_import_fails(arch):
    with pytest.raises(AssertionError, match='must import'):
        arch.check({'a': can_import('c')})


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
    arch.check({'a': [can_import('b'), must_not_import('c')]})


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
