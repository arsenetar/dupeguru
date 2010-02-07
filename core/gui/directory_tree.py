# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-02-06
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsgui.tree import Tree, Node

from ..directories import STATE_NORMAL, STATE_REFERENCE, STATE_EXCLUDED
from .base import GUIObject

STATE_ORDER = [STATE_NORMAL, STATE_REFERENCE, STATE_EXCLUDED]

# Lazily loads children
class DirectoryNode(Node):
    def __init__(self, app, path, name):
        Node.__init__(self, name)
        self._app = app
        self._directory_path = path
        self._loaded = False
        self._state = STATE_ORDER.index(self._app.directories.get_state(path))
    
    def __len__(self):
        if not self._loaded:
            self._load()
        return Node.__len__(self)
    
    def _load(self):
        self.clear()
        subpaths = self._app.directories.get_subfolders(self._directory_path)
        for path in subpaths:
            self.append(DirectoryNode(self._app, path, path[-1]))
        self._loaded = True
    
    # The state propery is an index to the combobox
    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, value):
        if value == self._state:
            return
        self._state = value
        state = STATE_ORDER[value]
        self._app.directories.set_state(self._directory_path, state)
    

class DirectoryTree(GUIObject, Tree):
    def __init__(self, view, app):
        GUIObject.__init__(self, view, app)
        Tree.__init__(self)
        self.connect()
        self._refresh()
        self.view.refresh()
    
    def _refresh(self):
        self.clear()
        for path in self.app.directories:
            self.append(DirectoryNode(self.app, path, unicode(path)))
    
    def add_directory(self, path):
        self.app.add_directory(path)
    
    #--- Event Handlers
    def directories_changed(self):
        self._refresh()
        self.view.refresh()
    
