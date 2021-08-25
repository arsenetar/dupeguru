# Created By: Virgil Dupras
# Created On: 2010-04-12
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.gui.table import GUITable, Row
from hscommon.gui.column import Column, Columns
from hscommon.trans import trget

coltr = trget("columns")


class ProblemTable(GUITable):
    COLUMNS = [
        Column("path", coltr("File Path")),
        Column("msg", coltr("Error Message")),
    ]

    def __init__(self, problem_dialog):
        GUITable.__init__(self)
        self._columns = Columns(self)
        self.dialog = problem_dialog

    # --- Override
    def _update_selection(self):
        row = self.selected_row
        dupe = row.dupe if row is not None else None
        self.dialog.select_dupe(dupe)

    def _fill(self):
        problems = self.dialog.app.results.problems
        for dupe, msg in problems:
            self.append(ProblemRow(self, dupe, msg))


class ProblemRow(Row):
    def __init__(self, table, dupe, msg):
        Row.__init__(self, table)
        self.dupe = dupe
        self.msg = msg
        self.path = str(dupe.path)
