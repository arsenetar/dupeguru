# Created By: Virgil Dupras
# Created On: 2010-04-12
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QLabel,
    QTableView,
    QAbstractItemView,
    QWidget,
)

from core.gui.problem_dialog import ProblemDialog as ProblemDiaglogModel
from qt.util import move_to_screen_center
from hscommon.trans import trget
from qt.problem_table import ProblemTable

tr = trget("ui")


class ProblemDialog(QDialog):
    def __init__(self, parent: QWidget, model: ProblemDiaglogModel, **kwargs) -> None:
        flags = Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowSystemMenuHint
        super().__init__(parent, flags, **kwargs)
        self.model = model
        self.table_view = QTableView(self)
        self.table = ProblemTable(self.model.problem_table, view=self.table_view)
        self._setupUi()

    def _setupUi(self) -> None:
        self.setWindowTitle(tr("Problems!"))
        self.resize(413, 323)
        main_layout = QVBoxLayout(self)
        notice_label = QLabel(self)
        msg = tr(
            "There were problems processing some (or all) of the files. The cause of "
            "these problems are described in the table below. Those files were not "
            "removed from your results."
        )
        notice_label.setText(msg)
        notice_label.setWordWrap(True)
        main_layout.addWidget(notice_label)

        self.table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setShowGrid(False)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.verticalHeader().setDefaultSectionSize(18)
        self.table_view.verticalHeader().setHighlightSections(False)
        main_layout.addWidget(self.table_view)

        button_layout = QHBoxLayout()
        reveal_button = QPushButton(self)
        reveal_button.setText(tr("Reveal Selected"))
        button_layout.addWidget(reveal_button)

        spacer_item = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        button_layout.addItem(spacer_item)

        close_button = QPushButton(self)
        close_button.setText(tr("Close"))
        close_button.setDefault(True)
        button_layout.addWidget(close_button)

        main_layout.addLayout(button_layout)

        reveal_button.clicked.connect(self.model.reveal_selected_dupe)
        close_button.clicked.connect(self.accept)

    def showEvent(self, event: QShowEvent) -> None:
        # have to do this here as the frameGeometry is not correct until shown
        move_to_screen_center(self)
        super().showEvent(event)
