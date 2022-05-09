# Created By: Virgil Dupras
# Created On: 2011-09-06
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt, QMimeData, QByteArray
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QListView,
    QDialogButtonBox,
    QAbstractItemView,
    QLabel,
    QStyle,
    QSplitter,
    QWidget,
    QSizePolicy,
)

from hscommon.trans import trget
from qt.selectable_list import ComboboxModel, ListviewModel
from qt.util import vertical_spacer
from core.gui.prioritize_dialog import PrioritizeDialog as PrioritizeDialogModel

tr = trget("ui")

MIME_INDEXES = "application/dupeguru.rowindexes"


class PrioritizationList(ListviewModel):
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled

    # --- Drag & Drop
    def dropMimeData(self, mime_data, action, row, column, parent_index):
        if not mime_data.hasFormat(MIME_INDEXES):
            return False
        # Since we only drop in between items, parentIndex must be invalid, and we use the row arg
        # to know where the drop took place.
        if parent_index.isValid():
            return False
        # "When row and column are -1 it means that the dropped data should be considered as
        # dropped directly on parent."
        # Moving items to row -1 would put them before the last item. Fix the row to drop the
        # dragged items after the last item.
        if row < 0:
            row = len(self.model) - 1
        str_mime_data = bytes(mime_data.data(MIME_INDEXES)).decode()
        indexes = list(map(int, str_mime_data.split(",")))
        self.model.move_indexes(indexes, row)
        self.view.selectionModel().clearSelection()
        return True

    def mimeData(self, indexes):
        rows = {str(index.row()) for index in indexes}
        data = ",".join(rows)
        mime_data = QMimeData()
        mime_data.setData(MIME_INDEXES, QByteArray(data.encode()))
        return mime_data

    def mimeTypes(self):
        return [MIME_INDEXES]

    def supportedDropActions(self):
        return Qt.MoveAction


class PrioritizeDialog(QDialog):
    def __init__(self, parent, app, **kwargs):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        super().__init__(parent, flags, **kwargs)
        self._setupUi()
        self.model = PrioritizeDialogModel(app=app.model)
        self.categoryList = ComboboxModel(model=self.model.category_list, view=self.categoryCombobox)
        self.criteriaList = ListviewModel(model=self.model.criteria_list, view=self.criteriaListView)
        self.prioritizationList = PrioritizationList(
            model=self.model.prioritization_list, view=self.prioritizationListView
        )
        self.model.view = self

        self.addCriteriaButton.clicked.connect(self.model.add_selected)
        self.criteriaListView.doubleClicked.connect(self.model.add_selected)
        self.removeCriteriaButton.clicked.connect(self.model.remove_selected)
        self.prioritizationListView.doubleClicked.connect(self.model.remove_selected)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def _setupUi(self):
        self.setWindowTitle(tr("Re-Prioritize duplicates"))
        self.resize(700, 400)

        # widgets
        msg = tr(
            "Add criteria to the right box and click OK to send the dupes that correspond the "
            "best to these criteria to their respective group's "
            "reference position. Read the help file for more information."
        )
        self.promptLabel = QLabel(msg)
        self.promptLabel.setWordWrap(True)
        self.categoryCombobox = QComboBox()
        self.criteriaListView = QListView()
        self.criteriaListView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.addCriteriaButton = QPushButton(self.style().standardIcon(QStyle.SP_ArrowRight), "")
        self.removeCriteriaButton = QPushButton(self.style().standardIcon(QStyle.SP_ArrowLeft), "")
        self.prioritizationListView = QListView()
        self.prioritizationListView.setAcceptDrops(True)
        self.prioritizationListView.setDragEnabled(True)
        self.prioritizationListView.setDragDropMode(QAbstractItemView.InternalMove)
        self.prioritizationListView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.prioritizationListView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        # layout
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addWidget(self.promptLabel)
        self.splitter = QSplitter()
        sp = self.splitter.sizePolicy()
        sp.setVerticalPolicy(QSizePolicy.Expanding)
        self.splitter.setSizePolicy(sp)
        self.leftSide = QWidget()
        self.leftWidgetsLayout = QVBoxLayout()
        self.leftWidgetsLayout.addWidget(self.categoryCombobox)
        self.leftWidgetsLayout.addWidget(self.criteriaListView)
        self.leftSide.setLayout(self.leftWidgetsLayout)
        self.splitter.addWidget(self.leftSide)
        self.rightSide = QWidget()
        self.rightWidgetsLayout = QHBoxLayout()
        self.addRemoveButtonsLayout = QVBoxLayout()
        self.addRemoveButtonsLayout.addItem(vertical_spacer())
        self.addRemoveButtonsLayout.addWidget(self.addCriteriaButton)
        self.addRemoveButtonsLayout.addWidget(self.removeCriteriaButton)
        self.addRemoveButtonsLayout.addItem(vertical_spacer())
        self.rightWidgetsLayout.addLayout(self.addRemoveButtonsLayout)
        self.rightWidgetsLayout.addWidget(self.prioritizationListView)
        self.rightSide.setLayout(self.rightWidgetsLayout)
        self.splitter.addWidget(self.rightSide)
        self.mainLayout.addWidget(self.splitter)
        self.mainLayout.addWidget(self.buttonBox)
