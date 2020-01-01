# Created By: Virgil Dupras
# Created On: 2009-05-17
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt, QAbstractTableModel
from PyQt5.QtWidgets import QHeaderView, QTableView

from hscommon.trans import trget

tr = trget("ui")

HEADER = [tr("Attribute"), tr("Selected"), tr("Reference")]


class DetailsModel(QAbstractTableModel):
    def __init__(self, model, **kwargs):
        super().__init__(**kwargs)
        self.model = model

    def columnCount(self, parent):
        return len(HEADER)

    def data(self, index, role):
        if not index.isValid():
            return None
        if role != Qt.DisplayRole:
            return None
        column = index.column()
        row = index.row()
        return self.model.row(row)[column]

    def headerData(self, section, orientation, role):
        if (
            orientation == Qt.Horizontal
            and role == Qt.DisplayRole
            and section < len(HEADER)
        ):
            return HEADER[section]
        return None

    def rowCount(self, parent):
        return self.model.row_count()


class DetailsTable(QTableView):
    def __init__(self, *args):
        QTableView.__init__(self, *args)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setShowGrid(False)

    def setModel(self, model):
        QTableView.setModel(self, model)
        # The model needs to be set to set header stuff
        hheader = self.horizontalHeader()
        hheader.setHighlightSections(False)
        hheader.setStretchLastSection(False)
        hheader.resizeSection(0, 100)
        hheader.setSectionResizeMode(0, QHeaderView.Fixed)
        hheader.setSectionResizeMode(1, QHeaderView.Stretch)
        hheader.setSectionResizeMode(2, QHeaderView.Stretch)
        vheader = self.verticalHeader()
        vheader.setVisible(False)
        vheader.setDefaultSectionSize(18)
