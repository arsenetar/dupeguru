# Created By: Virgil Dupras
# Created On: 2011-09-06
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QListView,
    QDialogButtonBox)

from hscommon.trans import tr
from qtlib.selectable_list import ComboboxModel, ListviewModel
from core.gui.prioritize_dialog import PrioritizeDialog as PrioritizeDialogModel

class PrioritizeDialog(QDialog):
    def __init__(self, parent, app):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        QDialog.__init__(self, parent, flags)
        self.app = app
        self._setupUi()
        self.model = PrioritizeDialogModel(view=self, app=app)
        self.categoryList = ComboboxModel(model=self.model.category_list, view=self.categoryCombobox)
        self.criteriaList = ListviewModel(model=self.model.criteria_list, view=self.criteriaListView)
        self.prioritizationList = ListviewModel(model=self.model.prioritization_list, view=self.prioritizationListView)
        
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
