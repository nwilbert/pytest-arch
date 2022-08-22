from pathlib import Path

import pytest

from pyarch.model import DotPath, ImportInModule, ModuleNode, RootNode


@pytest.mark.parametrize(
    'path, parts',
    [
        (None, tuple()),
        ('', tuple()),
        ('aa', ('aa',)),
        ('a.b', ('a', 'b')),
        ('ab.cd.e', ('ab', 'cd', 'e')),
        ('ab..cd', ('ab', '', 'cd')),
        ([], tuple()),
        (['a', 'b'], ('a', 'b')),
        (DotPath('a.b'), ('a', 'b')),
        (DotPath(''), tuple()),
    ],
)
def test_dotpath_init(path: str, parts: tuple[str, ...]):
    assert DotPath(path).parts == parts


@pytest.mark.parametrize(
    'path, dotpath',
    [
        (Path(), DotPath()),
        (Path('aa') / 'bb', DotPath('aa.bb')),
        (Path('a.py'), DotPath('a')),
        (Path('a') / 'b.py', DotPath('a.b')),
        (Path('a') / '__init__.py', DotPath('a')),
        (Path('a.b') / 'c', DotPath(('a.b', 'c'))),
    ],
)
def test_dotpath_from_path(path: Path, dotpath: DotPath):
    assert DotPath.from_path(path) == dotpath


@pytest.mark.parametrize(
    'path, other, result',
    [
        ('', '', True),
        ('a', 'a', True),
        ('a.b', 'a', True),
        ('aa.b', 'aa.b', True),
        ('b.b', 'a.b', False),
        ('a.b', 'b', False),
        ('ab.cd.e', 'ab.cd', True),
        ('e.ab.cd', 'ab.cd', False),
    ],
)
def test_dotpath_is_relative_to(path: str, other: str, result: bool):
    assert DotPath(path).is_relative_to(DotPath(other)) == result


def test_dotpath_name():
    assert DotPath('a.bb').name == 'bb'


def test_dotpath_name_index_error():
    with pytest.raises(IndexError):
        _ = DotPath().name


@pytest.mark.parametrize(
    'dotpath, parent',
    [
        (DotPath('aa'), DotPath()),
        (DotPath('aa.bb.cc'), DotPath('aa.bb')),
        (DotPath(), DotPath()),
    ],
)
def test_dotpath_parent(dotpath: DotPath, parent: DotPath):
    assert dotpath.parent == parent


def test_dotpath_str():
    assert str(DotPath('ab.cd.e')) == 'ab.cd.e'


def test_dotpath_repr():
    assert repr(DotPath('ab.cd.e')) == "DotPath(('ab', 'cd', 'e'))"


def test_dotpath_equal():
    assert DotPath('ab.cd.e') == DotPath('ab.cd.e')
    assert DotPath('ab.cd.e') != DotPath('ab.d.e')


def test_dotpath_truediv():
    assert DotPath('a.b') / DotPath('c') == DotPath('a.b.c')
    assert DotPath('a') / 'b' == DotPath('a.b')
    assert 'a' / DotPath('b') == DotPath('a.b')


@pytest.fixture
def tree_base_node():
    base_node = RootNode()
    base_node.get_or_add(DotPath('1'), Path('1'))
    base_node.get_or_add(DotPath('2'), Path('2'))
    base_node.get_or_add(DotPath('2.1'), Path('1', '2'))
    return base_node


@pytest.mark.parametrize(
    'path_str, result_name',
    [
        ('1', '1'),
        ('2', '2'),
        ('2.1', '1'),
    ],
)
def test_node_get(tree_base_node, path_str, result_name):
    assert tree_base_node.get(DotPath(path_str)).name == result_name


def test_node_get_nested(tree_base_node):
    assert tree_base_node.get(DotPath('2')).get(DotPath('1')).name == '1'


def test_node_get_non_existend(tree_base_node):
    assert tree_base_node.get(DotPath('1.1')) is None


def test_node_get_root(tree_base_node):
    with pytest.raises(Exception):
        assert tree_base_node.get(DotPath())


def test_node_get_or_add_root():
    root_node = RootNode()
    new_node = root_node.get_or_add(DotPath('a'), Path('a'))
    assert new_node.name == 'a'
    assert new_node.file_path == Path('a')
    assert root_node.get(DotPath('a')).name == 'a'


def test_node_get_or_add_new_parent(tree_base_node):
    new_node = tree_base_node.get_or_add(DotPath('1.a.b'), Path('1', 'a', 'b'))
    assert new_node.name == 'b'
    assert new_node.file_path == Path('1', 'a', 'b')
    new_parent_node = tree_base_node.get(DotPath('1.a'))
    assert new_parent_node.name == 'a'
    assert new_parent_node.file_path == Path('1', 'a')
    assert new_parent_node.get(DotPath('b')).name == 'b'


def test_node_add_imports():
    imports = [
        ImportInModule(DotPath('a'), line_no=1),
        ImportInModule(DotPath('b'), line_no=2),
    ]
    node = ModuleNode('x', Path('foobar'))
    assert len(node.imports) == 0
    node.add_imports(imports)
    assert len(node.imports) == 2
    assert {str(import_of.import_path) for import_of in node.imports} == {
        'a',
        'b',
    }


def test_node_for_init_file():
    imports = [
        ImportInModule(DotPath('a'), line_no=1),
        ImportInModule(DotPath('b'), line_no=2),
    ]
    node = ModuleNode('x', Path('foobar'))
    assert node.file_path.name == 'foobar'
    assert len(node.imports) == 0
    node.add_data_for_init_file(imports)
    assert len(node.imports) == 2
    assert node.file_path == Path('foobar') / '__init__.py'


def test_node_walk():
    base_node = ModuleNode('base', Path())
    base_node.get_or_add(DotPath('a.c'), Path())
    base_node.get_or_add(DotPath('a.b.x'), Path())
    visited = [node.name for node in base_node.walk()]
    assert len(visited) == 5
    assert set(visited) == {'base', 'a', 'c', 'b', 'x'}
