# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import re
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import (
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QGridLayout,
    QDialog,
    QTableView,
    QAbstractItemView,
    QSpacerItem,
    QSizePolicy,
    QHeaderView,
)
from .exclude_list_table import ExcludeListTable

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
        self._row_matched = False  # test if at least one row matched our test string
        self._input_styled = False

        self.buttonAdd.clicked.connect(self.addStringFromLineEdit)
        self.buttonRemove.clicked.connect(self.removeSelected)
        self.buttonRestore.clicked.connect(self.restoreDefaults)
        self.buttonClose.clicked.connect(self.accept)
        self.buttonHelp.clicked.connect(self.display_help_message)
        self.buttonTestString.clicked.connect(self.onTestStringButtonClicked)
        self.inputLine.textEdited.connect(self.reset_input_style)
        self.testLine.textEdited.connect(self.reset_input_style)
        self.testLine.textEdited.connect(self.reset_table_style)

    def _setupUI(self):
        layout = QVBoxLayout(self)
        gridlayout = QGridLayout()
        self.buttonAdd = QPushButton(tr("Add"))
        self.buttonRemove = QPushButton(tr("Remove Selected"))
        self.buttonRestore = QPushButton(tr("Restore defaults"))
        self.buttonTestString = QPushButton(tr("Test string"))
        self.buttonClose = QPushButton(tr("Close"))
        self.buttonHelp = QPushButton(tr("Help"))
        self.inputLine = QLineEdit()
        self.testLine = QLineEdit()
        self.tableView = QTableView()
        triggers = (
            QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed | QAbstractItemView.SelectedClicked
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
        gridlayout.addWidget(self.inputLine, 0, 0)
        gridlayout.addWidget(self.buttonAdd, 0, 1, Qt.AlignLeft)
        gridlayout.addWidget(self.buttonRemove, 1, 1, Qt.AlignLeft)
        gridlayout.addWidget(self.buttonRestore, 2, 1, Qt.AlignLeft)
        gridlayout.addWidget(self.buttonHelp, 3, 1, Qt.AlignLeft)
        gridlayout.addWidget(self.buttonClose, 4, 1)
        gridlayout.addWidget(self.tableView, 1, 0, 6, 1)
        gridlayout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), 4, 1)
        gridlayout.addWidget(self.buttonTestString, 6, 1)
        gridlayout.addWidget(self.testLine, 6, 0)

        layout.addLayout(gridlayout)
        self.inputLine.setPlaceholderText(tr("Type a python regular expression here..."))
        self.inputLine.setFocus()
        self.testLine.setPlaceholderText(tr("Type a file system path or filename here..."))
        self.testLine.setClearButtonEnabled(True)

    # --- model --> view
    def show(self):
        super().show()
        self.inputLine.setFocus()

    @pyqtSlot()
    def addStringFromLineEdit(self):
        text = self.inputLine.text()
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
        self.inputLine.clear()

    def removeSelected(self):
        self.model.remove_selected()

    def restoreDefaults(self):
        self.model.restore_defaults()

    def onTestStringButtonClicked(self):
        input_text = self.testLine.text()
        if not input_text:
            self.reset_input_style()
            return
        # If at least one row matched, we know whether table is highlighted or not
        self._row_matched = self.model.test_string(input_text)
        self.table.refresh()

        # Test the string currently in the input text box as well
        input_regex = self.inputLine.text()
        if not input_regex:
            self.reset_input_style()
            return
        compiled = None
        try:
            compiled = re.compile(input_regex)
        except re.error:
            self.reset_input_style()
            return
        if self.model.is_match(input_text, compiled):
            self.inputLine.setStyleSheet("background-color: rgb(10, 200, 10);")
            self._input_styled = True
        else:
            self.reset_input_style()

    def reset_input_style(self):
        """Reset regex input line background"""
        if self._input_styled:
            self.inputLine.setStyleSheet(self.styleSheet())
            self._input_styled = False

    def reset_table_style(self):
        if self._row_matched:
            self._row_matched = False
            self.model.reset_rows_highlight()
        self.table.refresh()

    def display_help_message(self):
        self.app.show_message(
            tr(
                """\
These (case sensitive) python regular expressions will filter out files during scans.<br>\
Directores will also have their <strong>default state</strong> set to Excluded \
in the Directories tab if their name happens to match one of the selected regular expressions.<br>\
For each file collected, two tests are performed to determine whether or not to completely ignore it:<br>\
<li>1. Regular expressions with no path separator in them will be compared to the file name only.</li>
<li>2. Regular expressions with at least one path separator in them will be compared to the full path to the file.</li><br>
Example: if you want to filter out .PNG files from the "My Pictures" directory only:<br>\
<code>.*My\\sPictures\\\\.*\\.png</code><br><br>\
You can test the regular expression with the "test string" button after pasting a fake path in the test field:<br>\
<code>C:\\\\User\\My Pictures\\test.png</code><br><br>
Matching regular expressions will be highlighted.<br>\
If there is at least one highlight, the path or filename tested will be ignored during scans.<br><br>\
Directories and files starting with a period '.' are filtered out by default.<br><br>"""
            )
        )
