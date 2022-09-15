import pytest

from pyarch.model import DotPath
from pyarch.query import ImportOf, ModulesAt


@pytest.mark.parametrize(
    'project_structure',
    [
        {
            'a.py': 'from b import x',
        }
    ],
)
def test_contains_flat(arch_root_node):
    a = arch_root_node.get(DotPath('a'))
    assert ImportOf(DotPath('b')) in ModulesAt(a)
    assert ImportOf(DotPath('b.x')) in ModulesAt(a)
    assert ImportOf(DotPath('c')) not in ModulesAt(a)
    assert ImportOf(DotPath('b.y')) not in ModulesAt(a)


@pytest.mark.parametrize(
    'project_structure',
    [{'d': {'e.py': 'import x'}}],
)
def test_contains_nested(arch_root_node):
    d = arch_root_node.get(DotPath('d'))
    assert ImportOf(DotPath('x')) in ModulesAt(d)
    assert ImportOf(DotPath('y')) not in ModulesAt(d)


@pytest.mark.parametrize(
    'project_structure',
    [{'a.py': ''}],
)
def test_contains_with_wrong_type(arch):
    with pytest.raises(NotImplementedError):
        assert 42 in arch.modules_at('a')


@pytest.mark.parametrize(
    'project_structure',
    [{'d': {'a.py': 'import x', 'b.py': 'import y'}}],
)
def test_explain_contains_false(arch_root_node):
    d = arch_root_node.get(DotPath('d'))
    lines = ModulesAt(d).explain_why_contains_is_false(ImportOf(DotPath('z')))
    assert len(lines) == 2
    assert 'no matching' in lines[0]
    assert 'no matching' in lines[1]
    assert 'a.py' in lines[0]
    assert 'b.py' in lines[1]


@pytest.mark.parametrize(
    'project_structure',
    [
        {'r': {'a.py': 'import x', '__init__.py': 'import x'}},
    ],
)
def test_explain_contains_false_with_init(arch_root_node):
    r = arch_root_node.get(DotPath('r'))
    lines = ModulesAt(r).explain_why_contains_is_false(ImportOf(DotPath('y')))
    assert len(lines) == 2
    assert '__init__.py' in lines[0]


@pytest.mark.parametrize(
    'project_structure',
    [
        {
            'a.py': """
                import x.y
                import x.z
            """
        }
    ],
)
def test_explain_contains_true(arch_root_node):
    a = arch_root_node.get(DotPath('a'))
    lines = ModulesAt(a).explain_why_contains_is_true(ImportOf(DotPath('x')))
    assert len(lines) == 2
    assert 'found import of x' in lines[0]
    assert 'a.py:1' in lines[0]
    assert 'found import of x' in lines[1]
    assert 'a.py:2' in lines[1]


@pytest.mark.parametrize(
    'project_structure, absolute, n_lines',
    [
        ({'a.py': 'import x'}, True, 1),
        ({'a.py': 'from . import x'}, True, 0),
        ({'a.py': 'import x'}, False, 0),
        ({'a.py': 'from . import x'}, False, 1),
        ({'a.py': 'import x'}, None, 1),
        ({'a.py': 'from . import x'}, None, 1),
    ],
)
def test_explain_contains_true_with_absolute(
    arch_root_node, absolute, n_lines
):
    a = arch_root_node.get(DotPath('a'))
    lines = ModulesAt(a).explain_why_contains_is_true(
        ImportOf(DotPath('x'), absolute=absolute)
    )
    assert len(lines) == n_lines


@pytest.mark.parametrize(
    'project_structure',
    [
        {'r': {'a.py': 'import x', 'b.py': 'import x'}},
    ],
)
def test_explain_contains_true_with_exclude(arch_root_node):
    r = arch_root_node.get(DotPath('r'))
    lines = ModulesAt(r, exclude=[DotPath('b')]).explain_why_contains_is_true(
        ImportOf(DotPath('x'))
    )
    assert len(lines) == 1
    assert 'a.py' in lines[0]


@pytest.mark.parametrize(
    'project_structure',
    [
        {'r': {'a.py': 'import x', 'b.py': 'import x'}},
    ],
)
def test_explain_contains_false_with_exclude(arch_root_node):
    r = arch_root_node.get(DotPath('r'))
    lines = ModulesAt(r, exclude=[DotPath('b')]).explain_why_contains_is_false(
        ImportOf(DotPath('y'))
    )
    assert len(lines) == 1
    assert 'a.py' in lines[0]
