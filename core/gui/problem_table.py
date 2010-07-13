# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-04-12
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hscommon.notify import Listener
from hsgui.table import GUITable, Row

class ProblemTable(GUITable, Listener):
    def __init__(self, view, problem_dialog):
        GUITable.__init__(self)
        Listener.__init__(self, problem_dialog)
        self.view = view
        self.dialog = problem_dialog
    
    #--- Override
    def _update_selection(self):
        row = self.selected_row
        dupe = row.dupe if row is not None else None
        self.dialog.select_dupe(dupe)
    
    def _fill(self):
        problems = self.dialog.app.results.problems
        for dupe, msg in problems:
            self.append(ProblemRow(self, dupe, msg))
    
    #--- Event handlers
    def problems_changed(self):
        self.refresh()
        self.view.refresh()
    

class ProblemRow(Row):
    def __init__(self, table, dupe, msg):
        Row.__init__(self, table)
        self.dupe = dupe
        self.msg = msg
        self.path = unicode(dupe.path)
    
