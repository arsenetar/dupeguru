# Created By: Virgil Dupras
# Created On: 2010-02-05
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from .base import GUIObject

class DetailsPanel(GUIObject):
    def __init__(self, view, app):
        GUIObject.__init__(self, view, app)
        self._table = []
    
    def connect(self):
        GUIObject.connect(self)
        self._refresh()
        self.view.refresh()
    
    #--- Private
    def _refresh(self):
        if self.app.selected_dupes:
            dupe = self.app.selected_dupes[0]
            group = self.app.results.get_group_of_duplicate(dupe)
        else:
            dupe = None
            group = None
        data1 = self.app.get_display_info(dupe, group, False)
        # we don't want the two sides of the table to display the stats for the same file
        ref = group.ref if group is not None and group.ref is not dupe else None
        data2 = self.app.get_display_info(ref, group, False)
        columns = self.app.result_table.COLUMNS[1:] # first column is the 'marked' column
        self._table = [(c.display, data1[c.name], data2[c.name]) for c in columns]
    
    #--- Public
    def row_count(self):
        return len(self._table)
    
    def row(self, row_index):
        return self._table[row_index]
    
    #--- Event Handlers
    def dupes_selected(self):
        self._refresh()
        self.view.refresh()
    
