# Created By: Virgil Dupras
# Created On: 2010-02-06
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.gui.tree import Tree, Node

from ..directories import DirectoryState
from .base import DupeGuruGUIObject

STATE_ORDER = [DirectoryState.NORMAL, DirectoryState.REFERENCE, DirectoryState.EXCLUDED]


# Lazily loads children
class DirectoryNode(Node):
    def __init__(self, tree, path, name):
        Node.__init__(self, name)
        self._tree = tree
        self._directory_path = path
        self._loaded = False
        self._state = STATE_ORDER.index(self._tree.app.directories.get_state(path))

    def __len__(self):
        if not self._loaded:
            self._load()
        return Node.__len__(self)

    def _load(self):
        self.clear()
        subpaths = self._tree.app.directories.get_subfolders(self._directory_path)
        for path in subpaths:
            self.append(DirectoryNode(self._tree, path, path.name))
        self._loaded = True

    def update_all_states(self):
        self._state = STATE_ORDER.index(self._tree.app.directories.get_state(self._directory_path))
        for node in self:
            node.update_all_states()

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
        self._tree.app.directories.set_state(self._directory_path, state)
        self._tree.update_all_states()


class DirectoryTree(Tree, DupeGuruGUIObject):
    # --- model -> view calls:
    # refresh()
    # refresh_states() # when only states label need to be refreshed
    #
    def __init__(self, app):
        Tree.__init__(self)
        DupeGuruGUIObject.__init__(self, app)

    def _view_updated(self):
        self._refresh()
        self.view.refresh()

    def _refresh(self):
        self.clear()
        for path in self.app.directories:
            self.append(DirectoryNode(self, path, str(path)))

    def add_directory(self, path):
        self.app.add_directory(path)

    def remove_selected(self):
        selected_paths = self.selected_paths
        if not selected_paths:
            return
        to_delete = [path[0] for path in selected_paths if len(path) == 1]
        if to_delete:
            self.app.remove_directories(to_delete)
        else:
            # All selected nodes or on second-or-more level, exclude them.
            nodes = self.selected_nodes
            newstate = DirectoryState.EXCLUDED
            if all(node.state == DirectoryState.EXCLUDED for node in nodes):
                newstate = DirectoryState.NORMAL
            for node in nodes:
                node.state = newstate

    def select_all(self):
        self.selected_nodes = list(self)
        self.view.refresh()

    def update_all_states(self):
        for node in self:
            node.update_all_states()
        self.view.refresh_states()

    # --- Event Handlers
    def directories_changed(self):
        self._view_updated()
