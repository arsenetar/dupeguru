# Created By: Virgil Dupras
# Created On: 2010-04-12
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from qtlib.column import Column
from qtlib.table import Table

class ProblemTable(Table):
    COLUMNS = [
        Column('path', defaultWidth=150),
        Column('msg', defaultWidth=150),
    ]
    
    def __init__(self, model, view):
        Table.__init__(self, model, view)
        # we have to prevent Return from initiating editing.
        # self.view.editSelected = lambda: None
    