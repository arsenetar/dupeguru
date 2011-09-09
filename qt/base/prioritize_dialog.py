# Created By: Virgil Dupras
# Created On: 2011-09-06
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt, QMimeData, QByteArray
from PyQt4.QtGui import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QListView,
    QDialogButtonBox, QAbstractItemView)

from hscommon.trans import tr
from qtlib.selectable_list import ComboboxModel, ListviewModel
from core.gui.prioritize_dialog import PrioritizeDialog as PrioritizeDialogModel

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
        self.app = app
        self._setupUi()
        self.model = PrioritizeDialogModel(view=self, app=app)
        self.categoryList = ComboboxModel(model=self.model.category_list, view=self.categoryCombobox)
        self.criteriaList = ListviewModel(model=self.model.criteria_list, view=self.criteriaListView)
        self.prioritizationList = PrioritizationList(model=self.model.prioritization_list, view=self.prioritizationListView)
        
        self.addCriteriaButton.clicked.connect(self.model.add_selected)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def _setupUi(self):
        self.setWindowTitle(tr("Re-prioritize duplicates"))
        self.resize(413, 323)
        
        #widgets
        self.categoryCombobox = QComboBox()
        self.criteriaListView = QListView()
        self.addCriteriaButton = QPushButton("-->")
        self.prioritizationListView = QListView()
        self.prioritizationListView.setAcceptDrops(True)
        self.prioritizationListView.setDragEnabled(True)
        self.prioritizationListView.setDragDropMode(QAbstractItemView.InternalMove)
        self.prioritizationListView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        
        # layout
        self.mainLayout = QVBoxLayout(self)
        self.widgetsLayout = QHBoxLayout()
        self.leftWidgetsLayout = QVBoxLayout()
        self.leftWidgetsLayout.addWidget(self.categoryCombobox)
        self.leftWidgetsLayout.addWidget(self.criteriaListView)
        self.widgetsLayout.addLayout(self.leftWidgetsLayout)
        self.widgetsLayout.addWidget(self.addCriteriaButton)
        self.widgetsLayout.addWidget(self.prioritizationListView)
        self.mainLayout.addLayout(self.widgetsLayout)
        self.mainLayout.addWidget(self.buttonBox)
