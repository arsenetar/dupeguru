# Created By: Virgil Dupras
# Created On: 2011-09-06
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt, QMimeData, QByteArray
from PyQt4.QtGui import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QListView,
    QDialogButtonBox, QAbstractItemView, QLabel, QStyle, QSplitter, QWidget, QSizePolicy)

from hscommon.trans import trget
from qtlib.selectable_list import ComboboxModel, ListviewModel
from qtlib.util import verticalSpacer
from core.gui.prioritize_dialog import PrioritizeDialog as PrioritizeDialogModel

tr = trget('ui')

MIME_INDEXES = 'application/dupeguru.rowindexes'

class PrioritizationList(ListviewModel):
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
    
    #--- Drag & Drop
    def dropMimeData(self, mimeData, action, row, column, parentIndex):
        if not mimeData.hasFormat(MIME_INDEXES):
            return False
        # Since we only drop in between items, parentIndex must be invalid, and we use the row arg
        # to know where the drop took place.
        if parentIndex.isValid():
            return False
        strMimeData = bytes(mimeData.data(MIME_INDEXES)).decode()
        indexes = list(map(int, strMimeData.split(',')))
        self.model.move_indexes(indexes, row)
        return True
    
    def mimeData(self, indexes):
        rows = {str(index.row()) for index in indexes}
        data = ','.join(rows)
        mimeData = QMimeData()
        mimeData.setData(MIME_INDEXES, QByteArray(data.encode()))
        return mimeData
    
    def mimeTypes(self):
        return [MIME_INDEXES]
    
    def supportedDropActions(self):
        return Qt.MoveAction

class PrioritizeDialog(QDialog):
    def __init__(self, parent, app):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        QDialog.__init__(self, parent, flags)
        self._setupUi()
        self.model = PrioritizeDialogModel(app=app.model)
        self.categoryList = ComboboxModel(model=self.model.category_list, view=self.categoryCombobox)
        self.criteriaList = ListviewModel(model=self.model.criteria_list, view=self.criteriaListView)
        self.prioritizationList = PrioritizationList(model=self.model.prioritization_list, view=self.prioritizationListView)
        self.model.view = self
        
        self.addCriteriaButton.clicked.connect(self.model.add_selected)
        self.removeCriteriaButton.clicked.connect(self.model.remove_selected)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def _setupUi(self):
        self.setWindowTitle(tr("Re-Prioritize duplicates"))
        self.resize(700, 400)
        
        #widgets
        msg = tr("Add criteria to the right box and click OK to send the dupes that correspond the "
            "best to these criteria to their respective group's "
            "reference position. Read the help file for more information.")
        self.promptLabel = QLabel(msg)
        self.promptLabel.setWordWrap(True)
        self.categoryCombobox = QComboBox()
        self.criteriaListView = QListView()
        self.addCriteriaButton = QPushButton(self.style().standardIcon(QStyle.SP_ArrowRight), "")
        self.removeCriteriaButton = QPushButton(self.style().standardIcon(QStyle.SP_ArrowLeft), "")
        self.prioritizationListView = QListView()
        self.prioritizationListView.setAcceptDrops(True)
        self.prioritizationListView.setDragEnabled(True)
        self.prioritizationListView.setDragDropMode(QAbstractItemView.InternalMove)
        self.prioritizationListView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        
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
        self.addRemoveButtonsLayout.addItem(verticalSpacer())
        self.addRemoveButtonsLayout.addWidget(self.addCriteriaButton)
        self.addRemoveButtonsLayout.addWidget(self.removeCriteriaButton)
        self.addRemoveButtonsLayout.addItem(verticalSpacer())
        self.rightWidgetsLayout.addLayout(self.addRemoveButtonsLayout)
        self.rightWidgetsLayout.addWidget(self.prioritizationListView)
        self.rightSide.setLayout(self.rightWidgetsLayout)
        self.splitter.addWidget(self.rightSide)
        self.mainLayout.addWidget(self.splitter)
        self.mainLayout.addWidget(self.buttonBox)
