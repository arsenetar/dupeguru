# Created By: Virgil Dupras
# Created On: 2012-03-13
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QPushButton,
    QTableView,
    QAbstractItemView,
)

from hscommon.trans import trget
from qtlib.util import horizontalWrap
from .ignore_list_table import IgnoreListTable

tr = trget("ui")


class IgnoreListDialog(QDialog):
    def __init__(self, parent, model, **kwargs):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        super().__init__(parent, flags, **kwargs)
        self.specific_actions = frozenset()
        self._setupUi()
        self.model = model
        self.model.view = self
        self.table = IgnoreListTable(self.model.ignore_list_table, view=self.tableView)

        self.removeSelectedButton.clicked.connect(self.model.remove_selected)
        self.clearButton.clicked.connect(self.model.clear)
        self.closeButton.clicked.connect(self.accept)

    def _setupUi(self):
        self.setWindowTitle(tr("Ignore List"))
        self.resize(540, 330)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.tableView = QTableView()
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setShowGrid(False)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.verticalHeader().setDefaultSectionSize(18)
        self.tableView.verticalHeader().setHighlightSections(False)
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.setWordWrap(False)
        self.verticalLayout.addWidget(self.tableView)
        self.removeSelectedButton = QPushButton(tr("Remove Selected"))
        self.clearButton = QPushButton(tr("Clear"))
        self.closeButton = QPushButton(tr("Close"))
        self.verticalLayout.addLayout(
            horizontalWrap(
                [self.removeSelectedButton, self.clearButton, None, self.closeButton]
            )
        )

    # --- model --> view
    def show(self):
        super().show()
