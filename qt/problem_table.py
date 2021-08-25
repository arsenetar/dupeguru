# Created By: Virgil Dupras
# Created On: 2010-04-12
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from qtlib.column import Column
from qtlib.table import Table


class ProblemTable(Table):
    COLUMNS = [
        Column("path", default_width=150),
        Column("msg", default_width=150),
    ]

    def __init__(self, model, view, **kwargs):
        super().__init__(model, view, **kwargs)
        # we have to prevent Return from initiating editing.
        # self.view.editSelected = lambda: None
