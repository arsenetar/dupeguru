# Created By: Virgil Dupras
# Created On: 2012-03-13
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.gui.table import GUITable, Row
from hscommon.gui.column import Column, Columns
from hscommon.trans import trget

coltr = trget("columns")


class IgnoreListTable(GUITable):
    COLUMNS = [
        # the str concat below saves us needless localization.
        Column("path1", coltr("File Path") + " 1"),
        Column("path2", coltr("File Path") + " 2"),
    ]

    def __init__(self, ignore_list_dialog):
        GUITable.__init__(self)
        self._columns = Columns(self)
        self.view = None
        self.dialog = ignore_list_dialog

    # --- Override
    def _fill(self):
        for path1, path2 in self.dialog.ignore_list:
            self.append(IgnoreListRow(self, path1, path2))


class IgnoreListRow(Row):
    def __init__(self, table, path1, path2):
        Row.__init__(self, table)
        self.path1_original = path1
        self.path2_original = path2
        self.path1 = str(path1)
        self.path2 = str(path2)
