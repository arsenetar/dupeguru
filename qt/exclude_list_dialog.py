# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import (
    QPushButton, QLineEdit, QVBoxLayout, QGridLayout, QDialog,
    QTableView, QAbstractItemView, QSpacerItem, QSizePolicy, QHeaderView
)
from .exclude_list_table import ExcludeListTable, ExcludeView

from core.exclude import AlreadyThereException
from hscommon.trans import trget
tr = trget("ui")


class ExcludeListDialog(QDialog):
    def __init__(self, app, parent, model, **kwargs):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        super().__init__(parent, flags, **kwargs)
        self.app = app
        self.specific_actions = frozenset()
        self._setupUI()
        self.model = model  # ExcludeListDialogCore
        self.model.view = self
        self.table = ExcludeListTable(app, view=self.tableView)  # Qt ExcludeListTable

        self.buttonAdd.clicked.connect(self.addStringFromLineEdit)
        self.buttonRemove.clicked.connect(self.removeSelected)
        self.buttonRestore.clicked.connect(self.restoreDefaults)
        self.buttonClose.clicked.connect(self.accept)
        self.buttonHelp.clicked.connect(self.display_help_message)

    def _setupUI(self):
        layout = QVBoxLayout(self)
        gridlayout = QGridLayout()
        self.buttonAdd = QPushButton(tr("Add"))
        self.buttonRemove = QPushButton(tr("Remove Selected"))
        self.buttonRestore = QPushButton(tr("Restore defaults"))
        self.buttonClose = QPushButton(tr("Close"))
        self.buttonHelp = QPushButton(tr("Help"))
        self.linedit = QLineEdit()
        self.tableView = ExcludeView()
        triggers = (
            QAbstractItemView.DoubleClicked
            | QAbstractItemView.EditKeyPressed
            | QAbstractItemView.SelectedClicked
        )
        self.tableView.setEditTriggers(triggers)
        self.tableView.setSelectionMode(QTableView.ExtendedSelection)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        self.tableView.setShowGrid(False)
        vheader = self.tableView.verticalHeader()
        vheader.setSectionsMovable(True)
        vheader.setVisible(False)
        hheader = self.tableView.horizontalHeader()
        hheader.setSectionsMovable(False)
        hheader.setSectionResizeMode(QHeaderView.Fixed)
        hheader.setStretchLastSection(True)
        hheader.setHighlightSections(False)
        hheader.setVisible(True)
        gridlayout.addWidget(self.linedit, 0, 0)
        gridlayout.addWidget(self.buttonAdd, 0, 1, Qt.AlignLeft)
        gridlayout.addWidget(self.buttonRemove, 1, 1, Qt.AlignLeft)
        gridlayout.addWidget(self.buttonRestore, 2, 1, Qt.AlignLeft)
        gridlayout.addWidget(self.buttonHelp, 3, 1, Qt.AlignLeft)
        gridlayout.addWidget(self.tableView, 1, 0, 5, 1)
        gridlayout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), 4, 1)
        gridlayout.addWidget(self.buttonClose, 5, 1)
        layout.addLayout(gridlayout)
        self.linedit.setPlaceholderText("Type a regular expression here...")
        self.linedit.setFocus()

    # --- model --> view
    def show(self):
        super().show()
        self.linedit.setFocus()

    @pyqtSlot()
    def addStringFromLineEdit(self):
        text = self.linedit.text()
        if not text:
            return
        try:
            self.model.add(text)
        except AlreadyThereException:
            self.app.show_message("Expression already in the list.")
            return
        except Exception as e:
            self.app.show_message(f"Expression is invalid: {e}")
            return
        self.linedit.clear()

    def removeSelected(self):
        self.model.remove_selected()

    def restoreDefaults(self):
        self.model.restore_defaults()

    def display_help_message(self):
        self.app.show_message("""\
These python regular expressions will filter out files and directory paths \
specified here.\nDuring directory selection, paths filtered here will be added as \
"Skipped" by default, but regular files will be ignored altogether during scans.""")
