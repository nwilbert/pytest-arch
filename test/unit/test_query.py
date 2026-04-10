import pytest

from pytest_imports.model import DotPath
from pytest_imports.query import (
    _find_matching_imports,
    _find_matching_private_imports,
    _find_within_parent_imports,
    must_import,
    must_not_import,
    must_not_import_private,
    must_not_import_within_parent,
    project,
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


def test_project():
    p = project()
    assert p.path is None
    assert p.without == ()


def test_project_hashable():
    p = project()
    assert {p: 'value'}[p] == 'value'


def test_must_import_defaults():
    p = must_import('foo.bar')
    assert p.path == 'foo.bar'
    assert p.via is None


def test_must_import_via():
    assert must_import('foo', via='absolute').via == 'absolute'
    assert must_import('foo', via='relative').via == 'relative'


def test_must_not_import_defaults():
    p = must_not_import('foo.bar')
    assert p.path == 'foo.bar'
    assert p.via is None


def test_must_not_import_private_defaults():
    p = must_not_import_private()
    assert p.path is None


def test_must_not_import_private_with_path():
    p = must_not_import_private('foo')
    assert p.path == 'foo'


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': 'from b import x'}],
)
def test_find_matching_imports_flat(imports_root_node):
    a = imports_root_node.get(DotPath('a'))
    assert list(_find_matching_imports(a, [], DotPath('b'), None))
    assert list(_find_matching_imports(a, [], DotPath('b.x'), None))
    assert not list(_find_matching_imports(a, [], DotPath('c'), None))
    assert not list(_find_matching_imports(a, [], DotPath('b.y'), None))
    assert not list(_find_matching_imports(a, [], DotPath('b.x.y'), None))


@pytest.mark.parametrize(
    'project_structure',
    [{'d': {'e.py': 'import x'}}],
)
def test_find_matching_imports_nested(imports_root_node):
    d = imports_root_node.get(DotPath('d'))
    assert list(_find_matching_imports(d, [], DotPath('x'), None))
    assert not list(_find_matching_imports(d, [], DotPath('y'), None))


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': 'import x\nimport x.y'}],
)
def test_find_matching_imports_returns_line_numbers(imports_root_node):
    a = imports_root_node.get(DotPath('a'))
    matches = list(_find_matching_imports(a, [], DotPath('x'), None))
    assert len(matches) == 2
    assert matches[0][1].line_no == 1
    assert matches[1][1].line_no == 2


@pytest.mark.parametrize(
    ('project_structure', 'via', 'n_matches'),
    [
        ({'a.py': 'import x'}, 'absolute', 1),
        ({'a.py': 'from . import x'}, 'absolute', 0),
        ({'a.py': 'import x'}, 'relative', 0),
        ({'a.py': 'from . import x'}, 'relative', 1),
        ({'a.py': 'import x'}, None, 1),
        ({'a.py': 'from . import x'}, None, 1),
    ],
)
def test_find_matching_imports_via(imports_root_node, via, n_matches):
    a = imports_root_node.get(DotPath('a'))
    matches = list(_find_matching_imports(a, [], DotPath('x'), via))
    assert len(matches) == n_matches


@pytest.mark.parametrize(
    'project_structure',
    [{'r': {'a.py': 'import x', 'b.py': 'import x'}}],
)
def test_find_matching_imports_exclude(imports_root_node):
    r = imports_root_node.get(DotPath('r'))
    matches = list(_find_matching_imports(r, [DotPath('b')], DotPath('x'), None))
    assert len(matches) == 1
    assert 'a.py' in str(matches[0][0].file_path)


@pytest.mark.parametrize(
    'project_structure',
    [{'r': {'a.py': 'import x', 'b.py': 'import x'}}],
)
def test_find_matching_imports_multiple_exclude(imports_root_node):
    r = imports_root_node.get(DotPath('r'))
    matches = list(
        _find_matching_imports(r, [DotPath('a'), DotPath('b')], DotPath('x'), None)
    )
    assert len(matches) == 0


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': 'from b import _x'}],
)
def test_find_matching_private_imports_matches_private(imports_root_node):
    a = imports_root_node.get(DotPath('a'))
    assert list(_find_matching_private_imports(a, [], None))


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': 'from b import x'}],
)
def test_find_matching_private_imports_ignores_public(imports_root_node):
    a = imports_root_node.get(DotPath('a'))
    assert not list(_find_matching_private_imports(a, [], None))


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': 'from __future__ import annotations'}],
)
def test_find_matching_private_imports_ignores_future(imports_root_node):
    a = imports_root_node.get(DotPath('a'))
    assert not list(_find_matching_private_imports(a, [], None))


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': 'from b import _x\nfrom c import _y'}],
)
def test_find_matching_private_imports_path_filter(imports_root_node):
    a = imports_root_node.get(DotPath('a'))
    assert len(list(_find_matching_private_imports(a, [], 'b'))) == 1
    assert len(list(_find_matching_private_imports(a, [], 'c'))) == 1
    assert len(list(_find_matching_private_imports(a, [], None))) == 2


@pytest.mark.parametrize(
    'project_structure',
    [{'r': {'a.py': 'from b import _x', 'c.py': 'from d import y'}}],
)
def test_find_matching_private_imports_nested(imports_root_node):
    r = imports_root_node.get(DotPath('r'))
    matches = list(_find_matching_private_imports(r, [], None))
    assert len(matches) == 1
    assert 'a.py' in str(matches[0][0].file_path)


def test_must_not_import_within_parent():
    p = must_not_import_within_parent(via='absolute')
    assert p.via == 'absolute'


def test_must_not_import_within_parent_relative():
    p = must_not_import_within_parent(via='relative')
    assert p.via == 'relative'


@pytest.mark.parametrize(
    'project_structure',
    [{'pkg': {'a.py': 'from pkg.b import x', 'b.py': ''}}],
)
def test_find_within_parent_imports_catches_absolute(imports_root_node):
    pkg = imports_root_node.get(DotPath('pkg'))
    matches = list(_find_within_parent_imports(pkg, [], 'absolute'))
    assert len(matches) == 1
    assert 'a.py' in str(matches[0][0].file_path)


@pytest.mark.parametrize(
    'project_structure',
    [{'pkg': {'a.py': 'from .b import x', 'b.py': ''}}],
)
def test_find_within_parent_imports_ignores_relative(imports_root_node):
    pkg = imports_root_node.get(DotPath('pkg'))
    assert not list(_find_within_parent_imports(pkg, [], 'absolute'))


@pytest.mark.parametrize(
    'project_structure',
    [{'pkg': {'a.py': 'from .b import x', 'b.py': ''}}],
)
def test_find_within_parent_imports_catches_relative(imports_root_node):
    pkg = imports_root_node.get(DotPath('pkg'))
    matches = list(_find_within_parent_imports(pkg, [], 'relative'))
    assert len(matches) == 1


@pytest.mark.parametrize(
    'project_structure',
    [{'pkg': {'a.py': 'import external'}}],
)
def test_find_within_parent_imports_ignores_external(imports_root_node):
    pkg = imports_root_node.get(DotPath('pkg'))
    assert not list(_find_within_parent_imports(pkg, [], 'absolute'))


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': 'import external'}],
)
def test_find_within_parent_imports_skips_top_level_modules(imports_root_node):
    a = imports_root_node.get(DotPath('a'))
    assert not list(_find_within_parent_imports(a, [], 'absolute'))


@pytest.mark.parametrize(
    'project_structure',
    [{'pkg': {'a.py': '#\n\nfrom pkg.b import x', 'b.py': 'from pkg.a import y'}}],
)
def test_find_within_parent_imports_returns_line_numbers(imports_root_node):
    pkg = imports_root_node.get(DotPath('pkg'))
    matches = list(_find_within_parent_imports(pkg, [], 'absolute'))
    assert len(matches) == 2
    assert matches[0][1].line_no == 3
    assert matches[1][1].line_no == 1
