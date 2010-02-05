# Created By: Virgil Dupras
# Created On: 2009-04-27
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QPixmap

from base.details_dialog import DetailsDialog as DetailsDialogBase
from details_dialog_ui import Ui_DetailsDialog

class DetailsDialog(DetailsDialogBase, Ui_DetailsDialog):
    def __init__(self, parent, app):
        DetailsDialogBase.__init__(self, parent, app)
        self.selectedPixmap = None
        self.referencePixmap = None
    
    def _setupUi(self):
        self.setupUi(self)
    
    def _update(self):
        if not self.app.selected_dupes:
            return
        dupe = self.app.selected_dupes[0]
        group = self.app.results.get_group_of_duplicate(dupe)
        ref = group.ref
        
        self.selectedPixmap = QPixmap(unicode(dupe.path))
        if ref is dupe:
            self.referencePixmap = None
        else:
            self.referencePixmap = QPixmap(unicode(ref.path))
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
    
