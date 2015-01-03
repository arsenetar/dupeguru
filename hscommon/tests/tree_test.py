# Created By: Virgil Dupras
# Created On: 2010-02-12
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from ..testutil import eq_
from ..gui.tree import Tree, Node

def tree_with_some_nodes():
    t = Tree()
    t.append(Node('foo'))
    t.append(Node('bar'))
    t.append(Node('baz'))
    t[0].append(Node('sub1'))
    t[0].append(Node('sub2'))
    return t

def test_selection():
    t = tree_with_some_nodes()
    assert t.selected_node is None
    eq_(t.selected_nodes, [])
    assert t.selected_path is None
    eq_(t.selected_paths, [])

def test_select_one_node():
    t = tree_with_some_nodes()
    t.selected_node = t[0][0]
    assert t.selected_node is t[0][0]
    eq_(t.selected_nodes, [t[0][0]])
    eq_(t.selected_path, [0, 0])
    eq_(t.selected_paths, [[0, 0]])

def test_select_one_path():
    t = tree_with_some_nodes()
    t.selected_path = [0, 1]
    assert t.selected_node is t[0][1]

def test_select_multiple_nodes():
    t = tree_with_some_nodes()
    t.selected_nodes = [t[0], t[1]]
    eq_(t.selected_paths, [[0], [1]])

def test_select_multiple_paths():
    t = tree_with_some_nodes()
    t.selected_paths = [[0], [1]]
    eq_(t.selected_nodes, [t[0], t[1]])

def test_select_none_path():
    # setting selected_path to None clears the selection
    t = Tree()
    t.selected_path = None
    assert t.selected_path is None

def test_select_none_node():
    # setting selected_node to None clears the selection
    t = Tree()
    t.selected_node = None
    eq_(t.selected_nodes, [])

def test_clear_removes_selection():
    # When clearing a tree, we want to clear the selection as well or else we end up with a crash
    # when calling selected_paths.
    t = tree_with_some_nodes()
    t.selected_path = [0]
    t.clear()
    assert t.selected_node is None

def test_selection_override():
    # All selection changed pass through the _select_node() method so it's easy for subclasses to
    # customize the tree's behavior.
    class MyTree(Tree):
        called = False
        def _select_nodes(self, nodes):
            self.called = True
        
    
    t = MyTree()
    t.selected_paths = []
    assert t.called
    t.called = False
    t.selected_node = None
    assert t.called

def test_findall():
    t = tree_with_some_nodes()
    r = t.findall(lambda n: n.name.startswith('sub'))
    eq_(set(r), set([t[0][0], t[0][1]]))

def test_findall_dont_include_self():
    # When calling findall with include_self=False, the node itself is never evaluated.
    t = tree_with_some_nodes()
    del t._name # so that if the predicate is called on `t`, we crash
    r = t.findall(lambda n: not n.name.startswith('sub'), include_self=False) # no crash
    eq_(set(r), set([t[0], t[1], t[2]]))

def test_find_dont_include_self():
    # When calling find with include_self=False, the node itself is never evaluated.
    t = tree_with_some_nodes()
    del t._name # so that if the predicate is called on `t`, we crash
    r = t.find(lambda n: not n.name.startswith('sub'), include_self=False) # no crash
    assert r is t[0]

def test_find_none():
    # when find() yields no result, return None
    t = Tree()
    assert t.find(lambda n: False) is None # no StopIteration exception
