# Created By: Virgil Dupras
# Created On: 2009-04-27
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt, SIGNAL, QAbstractTableModel, QVariant
from PyQt4.QtGui import QDialog, QHeaderView, QPixmap

from base.details_table import DetailsModel
from details_dialog_ui import Ui_DetailsDialog

class DetailsDialog(QDialog, Ui_DetailsDialog):
    def __init__(self, parent, app):
        QDialog.__init__(self, parent, Qt.Tool)
        self.app = app
        self.selectedPixmap = None
        self.referencePixmap = None
        self.setupUi(self)
        self.model = DetailsModel(app)
        self.tableView.setModel(self.model)
        self.connect(app, SIGNAL('duplicateSelected()'), self.duplicateSelected)
    
    def _update(self):
        dupe = self.app.selected_dupe
        if dupe is None:
            return
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
        QDialog.show(self)
        self._update()
    
    #--- Events
    def duplicateSelected(self):
        if self.isVisible():
            self._update()
    
