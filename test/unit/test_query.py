import pytest

from pyarch.model import DotPath
from pyarch.query import (
    _find_matching_imports,
    can_import,
    must_not_import,
    scope,
)


def test_scope_hashable():
    s = scope('foo.bar')
    assert {s: 'value'}[s] == 'value'


def test_scope_without():
    s = scope('foo', without=['bar', 'baz'])
    assert s.without == ('bar', 'baz')


def test_scope_without_single_string():
    s = scope('foo', without='bar')
    assert s.without == ('bar',)


def test_can_import_defaults():
    p = can_import('foo.bar')
    assert p.path == 'foo.bar'
    assert p.via is None


def test_can_import_via():
    assert can_import('foo', via='absolute').via == 'absolute'
    assert can_import('foo', via='relative').via == 'relative'


def test_must_not_import_defaults():
    p = must_not_import('foo.bar')
    assert p.path == 'foo.bar'
    assert p.via is None


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': 'from b import x'}],
)
def test_find_matching_imports_flat(arch_root_node):
    a = arch_root_node.get(DotPath('a'))
    assert list(_find_matching_imports(a, [], DotPath('b'), None))
    assert list(_find_matching_imports(a, [], DotPath('b.x'), None))
    assert not list(_find_matching_imports(a, [], DotPath('c'), None))
    assert not list(_find_matching_imports(a, [], DotPath('b.y'), None))
    assert not list(_find_matching_imports(a, [], DotPath('b.x.y'), None))


@pytest.mark.parametrize(
    'project_structure',
    [{'d': {'e.py': 'import x'}}],
)
def test_find_matching_imports_nested(arch_root_node):
    d = arch_root_node.get(DotPath('d'))
    assert list(_find_matching_imports(d, [], DotPath('x'), None))
    assert not list(_find_matching_imports(d, [], DotPath('y'), None))


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': 'import x\nimport x.y'}],
)
def test_find_matching_imports_returns_line_numbers(arch_root_node):
    a = arch_root_node.get(DotPath('a'))
    matches = list(_find_matching_imports(a, [], DotPath('x'), None))
    assert len(matches) == 2
    assert matches[0][1].line_no == 1
    assert matches[1][1].line_no == 2


@pytest.mark.parametrize(
    'project_structure, via, n_matches',
    [
        ({'a.py': 'import x'}, 'absolute', 1),
        ({'a.py': 'from . import x'}, 'absolute', 0),
        ({'a.py': 'import x'}, 'relative', 0),
        ({'a.py': 'from . import x'}, 'relative', 1),
        ({'a.py': 'import x'}, None, 1),
        ({'a.py': 'from . import x'}, None, 1),
    ],
)
def test_find_matching_imports_via(arch_root_node, via, n_matches):
    a = arch_root_node.get(DotPath('a'))
    matches = list(_find_matching_imports(a, [], DotPath('x'), via))
    assert len(matches) == n_matches


@pytest.mark.parametrize(
    'project_structure',
    [{'r': {'a.py': 'import x', 'b.py': 'import x'}}],
)
def test_find_matching_imports_exclude(arch_root_node):
    r = arch_root_node.get(DotPath('r'))
    matches = list(_find_matching_imports(r, [DotPath('b')], DotPath('x'), None))
    assert len(matches) == 1
    assert 'a.py' in str(matches[0][0].file_path)


@pytest.mark.parametrize(
    'project_structure',
    [{'r': {'a.py': 'import x', 'b.py': 'import x'}}],
)
def test_find_matching_imports_multiple_exclude(arch_root_node):
    r = arch_root_node.get(DotPath('r'))
    matches = list(
        _find_matching_imports(r, [DotPath('a'), DotPath('b')], DotPath('x'), None)
    )
    assert len(matches) == 0
