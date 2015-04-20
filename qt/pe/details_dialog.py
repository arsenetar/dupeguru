# Created By: Virgil Dupras
# Created On: 2009-04-27
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QVBoxLayout, QAbstractItemView, QHBoxLayout, QLabel, QSizePolicy

from hscommon.trans import trget
from ..base.details_dialog import DetailsDialog as DetailsDialogBase
from ..base.details_table import DetailsTable

tr = trget('ui')

class DetailsDialog(DetailsDialogBase):
    def __init__(self, parent, app):
        DetailsDialogBase.__init__(self, parent, app)
        self.selectedPixmap = None
        self.referencePixmap = None
    
    def _setupUi(self):
        self.setWindowTitle(tr("Details"))
        self.resize(502, 295)
        self.setMinimumSize(QSize(250, 250))
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(4)
        self.selectedImage = QLabel(self)
        sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.selectedImage.sizePolicy().hasHeightForWidth())
        self.selectedImage.setSizePolicy(sizePolicy)
        self.selectedImage.setScaledContents(False)
        self.selectedImage.setAlignment(Qt.AlignCenter)
        self.horizontalLayout.addWidget(self.selectedImage)
        self.referenceImage = QLabel(self)
        sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.referenceImage.sizePolicy().hasHeightForWidth())
        self.referenceImage.setSizePolicy(sizePolicy)
        self.referenceImage.setAlignment(Qt.AlignCenter)
        self.horizontalLayout.addWidget(self.referenceImage)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tableView = DetailsTable(self)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy)
        self.tableView.setMinimumSize(QSize(0, 188))
        self.tableView.setMaximumSize(QSize(16777215, 190))
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setShowGrid(False)
        self.verticalLayout.addWidget(self.tableView)
    
    def _update(self):
        if not self.app.model.selected_dupes:
            return
        dupe = self.app.model.selected_dupes[0]
        group = self.app.model.results.get_group_of_duplicate(dupe)
        ref = group.ref
        
        self.selectedPixmap = QPixmap(str(dupe.path))
        if ref is dupe:
            self.referencePixmap = None
        else:
            self.referencePixmap = QPixmap(str(ref.path))
        self._updateImages()
    
    def _updateImages(self):
        if self.selectedPixmap is not None:
            target_size = self.selectedImage.size()
            scaledPixmap = self.selectedPixmap.scaled(target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.selectedImage.setPixmap(scaledPixmap)
        else:
            self.selectedImage.setPixmap(QPixmap())
        if self.referencePixmap is not None:
            target_size = self.referenceImage.size()
            scaledPixmap = self.referencePixmap.scaled(target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.referenceImage.setPixmap(scaledPixmap)
        else:
            self.referenceImage.setPixmap(QPixmap())
    
    #--- Override
    def resizeEvent(self, event):
        self._updateImages()
    
    def show(self):
        DetailsDialogBase.show(self)
        self._update()
    
    # model --> view
    def refresh(self):
        DetailsDialogBase.refresh(self)
        if self.isVisible():
            self._update()
    
