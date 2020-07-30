# Created By: Virgil Dupras
# Created On: 2009-05-17
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt, QAbstractTableModel
from PyQt5.QtWidgets import QHeaderView, QTableView
from PyQt5.QtGui import QFont, QBrush

from hscommon.trans import trget

tr = trget("ui")

HEADER = [tr("Selected"), tr("Reference")]


class DetailsModel(QAbstractTableModel):
    def __init__(self, model, app, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.prefs = app.prefs

    def columnCount(self, parent):
        return len(HEADER)

    def data(self, index, role):
        if not index.isValid():
            return None
        # Skip first value "Attribute"
        column = index.column() + 1
        row = index.row()

        ignored_fields = ["Dupe Count"]
        if (self.model.row(row)[0] in ignored_fields
                or self.model.row(row)[1] == "---"
                or self.model.row(row)[2] == "---"):
            if role != Qt.DisplayRole:
                return None
            return self.model.row(row)[column]

        if role == Qt.DisplayRole:
            return self.model.row(row)[column]
        if role == Qt.ForegroundRole and self.model.row(row)[1] != self.model.row(row)[2]:
            return QBrush(self.prefs.details_table_delta_foreground_color)
        if role == Qt.FontRole and self.model.row(row)[1] != self.model.row(row)[2]:
            font = QFont(self.model.view.font())  # or simply QFont()
            font.setBold(True)
            return font
        return None  # QVariant()

    def headerData(self, section, orientation, role):
        if (
            orientation == Qt.Horizontal
            and role == Qt.DisplayRole
            and section < len(HEADER)
        ):
            return HEADER[section]
        elif (
            orientation == Qt.Vertical
            and role == Qt.DisplayRole
            and section < self.model.row_count()
        ):
            # Read "Attribute" cell for horizontal header
            return self.model.row(section)[0]
        return None

    def rowCount(self, parent):
        return self.model.row_count()


class DetailsTable(QTableView):
    def __init__(self, *args):
        QTableView.__init__(self, *args)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.NoSelection)
        self.setShowGrid(False)
        self.setWordWrap(False)
        self.setCornerButtonEnabled(False)

    def setModel(self, model):
        QTableView.setModel(self, model)
        # The model needs to be set to set header stuff
        hheader = self.horizontalHeader()
        hheader.setHighlightSections(False)
        hheader.setSectionResizeMode(0, QHeaderView.Stretch)
        hheader.setSectionResizeMode(1, QHeaderView.Stretch)
        vheader = self.verticalHeader()
        vheader.setVisible(True)
        vheader.setDefaultSectionSize(18)
        # hardcoded value above is not ideal, perhaps resize to contents first?
        # vheader.setSectionResizeMode(QHeaderView.ResizeToContents)
        vheader.setSectionResizeMode(QHeaderView.Fixed)
        vheader.setSectionsMovable(True)
