# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-02-05
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog

from core.gui.details_panel import DetailsPanel

from .details_table import DetailsModel

class DetailsDialog(QDialog):
    def __init__(self, parent, app):
        QDialog.__init__(self, parent, Qt.Tool)
        self.app = app
        self.model = DetailsPanel(self, app)
        self._setupUi()
        if self.app.prefs.detailsWindowRect is not None:
            self.setGeometry(self.app.prefs.detailsWindowRect)
        self.tableModel = DetailsModel(self.model)
        # tableView is defined in subclasses
        self.tableView.setModel(self.tableModel)
        self.model.connect()
        
        self.app.willSavePrefs.connect(self.appWillSavePrefs)
    
    def _setupUi(self): # Virtual
        pass
    
    #--- Events
    def appWillSavePrefs(self):
        self.app.prefs.detailsWindowRect = self.geometry()
    
    #--- model --> view
    def refresh(self):
        self.tableModel.reset()
    
