# Copyright 2014 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from collections import MutableSequence

from .base import GUIObject

class Node(MutableSequence):
    """Pretty bland node implementation to be used in a :class:`Tree`.
    
    It has a :attr:`parent`, behaves like a list, its content being its children. Link integrity
    is somewhat enforced (adding a child to a node will set the child's :attr:`parent`, but that's
    pretty much as far as we go, integrity-wise. Nodes don't tend to move around much in a GUI
    tree). We don't even check for infinite node loops. Don't play around these grounds too much.

    Nodes are designed to be subclassed and given meaningful attributes (those you'll want to
    display in your tree view), but they all have a :attr:`name`, which is given on initialization.
    """
    def __init__(self, name):
        self._name = name
        self._parent = None
        self._path = None
        self._children = []
    
    def __repr__(self):
        return '<Node %r>' % self.name
    
    #--- MutableSequence overrides
    def __delitem__(self, key):
        self._children.__delitem__(key)
    
    def __getitem__(self, key):
        return self._children.__getitem__(key)
    
    def __len__(self):
        return len(self._children)
    
    def __setitem__(self, key, value):
        self._children.__setitem__(key, value)
    
    def append(self, node):
        self._children.append(node)
        node._parent = self
        node._path = None
    
    def insert(self, index, node):
        self._children.insert(index, node)
        node._parent = self
        node._path = None
    
    #--- Public
    def clear(self):
        """Clears the node of all its children.
        """
        del self[:]
    
    def find(self, predicate, include_self=True):
        """Return the first child to match ``predicate``.
        
        See :meth:`findall`.
        """
        try:
            return next(self.findall(predicate, include_self=include_self))
        except StopIteration:
            return None
    
    def findall(self, predicate, include_self=True):
        """Yield all children matching ``predicate``.
        
        :param predicate: ``f(node) --> bool``
        :param include_self: Whether we can return ``self`` or we return only children.
        """
        if include_self and predicate(self):
            yield self
        for child in self:
            for found in child.findall(predicate, include_self=True):
                yield found
    
    def get_node(self, index_path):
        """Returns the node at ``index_path``.
        
        :param index_path: a list of int indexes leading to our node. See :attr:`path`.
        """
        result = self
        if index_path:
            for index in index_path:
                result = result[index]
        return result
    
    def get_path(self, target_node):
        """Returns the :attr:`path` of ``target_node``.
        
        If ``target_node`` is ``None``, returns ``None``.
        """
        if target_node is None:
            return None
        return target_node.path
    
    @property
    def children_count(self):
        """Same as ``len(self)``.
        """
        return len(self)
    
    @property
    def name(self):
        """Name for the node, supplied on init.
        """
        return self._name
    
    @property
    def parent(self):
        """Parent of the node.
        
        If ``None``, we have a root node.
        """
        return self._parent
    
    @property
    def path(self):
        """A list of node indexes leading from the root node to ``self``.
        
        The path of a node is always related to its :attr:`root`. It's the sequences of index that
        we have to take to get to our node, starting from the root. For example, if
        ``node.path == [1, 2, 3, 4]``, it means that ``node.root[1][2][3][4] is node``.
        """
        if self._path is None:
            if self._parent is None:
                self._path = []
            else:
                self._path = self._parent.path + [self._parent.index(self)]
        return self._path
    
    @property
    def root(self):
        """Root node of current node.
        
        To get it, we recursively follow our :attr:`parent` chain until we have ``None``.
        """
        if self._parent is None:
            return self
        else:
            return self._parent.root
    

class Tree(Node, GUIObject):
    """Cross-toolkit GUI-enabled tree view.
    
    This class is a bit too thin to be used as a tree view controller out of the box and HS apps
    that subclasses it each add quite a bit of logic to it to make it workable. Making this more
    usable out of the box is a work in progress.
    
    This class is here (in addition to being a :class:`Node`) mostly to handle selection.
    
    Subclasses :class:`Node` (it is the root node of all its children) and :class:`.GUIObject`.
    """
    def __init__(self):
        Node.__init__(self, '')
        GUIObject.__init__(self)
        #: Where we store selected nodes (as a list of :class:`Node`)
        self._selected_nodes = []
    
    #--- Virtual
    def _select_nodes(self, nodes):
        """(Virtual) Customize node selection behavior.
        
        By default, simply set :attr:`_selected_nodes`.
        """
        self._selected_nodes = nodes
    
    #--- Override
    def _view_updated(self):
        self.view.refresh()
    
    def clear(self):
        self._selected_nodes = []
        Node.clear(self)
    
    #--- Public
    @property
    def selected_node(self):
        """Currently selected node.
        
        *:class:`Node`*. *get/set*.
        
        First of :attr:`selected_nodes`. ``None`` if empty.
        """
        return self._selected_nodes[0] if self._selected_nodes else None
    
    @selected_node.setter
    def selected_node(self, node):
        if node is not None:
            self._select_nodes([node])
        else:
            self._select_nodes([])
    
    @property
    def selected_nodes(self):
        """List of selected nodes in the tree.
        
        *List of :class:`Node`*. *get/set*.
        
        We use nodes instead of indexes to store selection because it's simpler when it's time to
        manage selection of multiple node levels.
        """
        return self._selected_nodes
    
    @selected_nodes.setter
    def selected_nodes(self, nodes):
        self._select_nodes(nodes)
    
    @property
    def selected_path(self):
        """Currently selected path.
        
        *:attr:`Node.path`*. *get/set*.
        
        First of :attr:`selected_paths`. ``None`` if empty.
        """
        return self.get_path(self.selected_node)
    
    @selected_path.setter
    def selected_path(self, index_path):
        if index_path is not None:
            self.selected_paths = [index_path]
        else:
            self._select_nodes([])
    
    @property
    def selected_paths(self):
        """List of selected paths in the tree.
        
        *List of :attr:`Node.path`*. *get/set*
        
        Computed from :attr:`selected_nodes`.
        """
        return list(map(self.get_path, self._selected_nodes))
    
    @selected_paths.setter
    def selected_paths(self, index_paths):
        nodes = []
        for path in index_paths:
            try:
                nodes.append(self.get_node(path))
            except IndexError:
                pass
        self._select_nodes(nodes)
    
