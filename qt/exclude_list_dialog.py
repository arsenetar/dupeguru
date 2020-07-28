# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import (
    QPushButton, QLineEdit, QVBoxLayout, QGridLayout, QDialog,
    QTableView, QAbstractItemView, QSpacerItem, QSizePolicy, QHeaderView
)
from .exclude_list_table import ExcludeListTable, ExcludeView

from hscommon.trans import trget
tr = trget("ui")


class ExcludeListDialog(QDialog):
    def __init__(self, app, parent, model, **kwargs):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        super().__init__(parent, flags, **kwargs)
        self.specific_actions = frozenset()
        self._setupUI()
        self.model = model  # ExcludeListDialogCore
        self.model.view = self
        self.table = ExcludeListTable(app, view=self.tableView)

        self.buttonAdd.clicked.connect(self.addItem)
        self.buttonRemove.clicked.connect(self.removeItem)
        self.buttonRestore.clicked.connect(self.restoreDefaults)
        self.buttonClose.clicked.connect(self.accept)

    def _setupUI(self):
        layout = QVBoxLayout(self)
        gridlayout = QGridLayout()
        self.buttonAdd = QPushButton(tr("Add"))
        self.buttonRemove = QPushButton(tr("Remove Selected"))
        self.buttonRestore = QPushButton(tr("Restore defaults"))
        self.buttonClose = QPushButton(tr("Close"))
        self.linedit = QLineEdit()
        self.tableView = ExcludeView()
        triggers = (
            QAbstractItemView.DoubleClicked
            | QAbstractItemView.EditKeyPressed
            | QAbstractItemView.SelectedClicked
        )
        self.tableView.setEditTriggers(triggers)
        self.tableView.horizontalHeader().setVisible(True)
        self.tableView.setSelectionMode(QTableView.ExtendedSelection)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        # vheader = self.tableView.verticalHeader()
        # vheader.setSectionsMovable(True)
        # vheader.setVisible(True)
        # vheader.setDefaultSectionSize(50)
        hheader = self.tableView.horizontalHeader()
        hheader.setSectionsMovable(False)
        hheader.setSectionResizeMode(QHeaderView.Fixed)
        hheader.setStretchLastSection(True)
        hheader.setHighlightSections(False)
        gridlayout.addWidget(self.linedit, 0, 0)
        gridlayout.addWidget(self.buttonAdd, 0, 1, Qt.AlignLeft)
        gridlayout.addWidget(self.buttonRemove, 1, 1, Qt.AlignLeft)
        gridlayout.addWidget(self.buttonRestore, 2, 1, Qt.AlignLeft)
        gridlayout.addWidget(self.tableView, 1, 0, 4, 1)
        gridlayout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), 3, 1)
        gridlayout.addWidget(self.buttonClose, 4, 1)
        layout.addLayout(gridlayout)

    # --- model --> view
    def show(self):
        super().show()

    @pyqtSlot()
    def addItem(self):
        text = self.linedit.text()
        if not text:
            return
        self.model.add(text)
        self.linedit.clear()

    def removeItem(self):
        self.model.remove_selected()

    def restoreDefaults(self):
        self.model.restore_defaults()
