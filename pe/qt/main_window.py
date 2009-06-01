#!/usr/bin/env python
# Unit Name: main_window
# Created By: Virgil Dupras
# Created On: 2009-05-23
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QMessageBox, QAction

from base.main_window import MainWindow as MainWindowBase

class MainWindow(MainWindowBase):
    def _setupUi(self):
        MainWindowBase._setupUi(self)
        self.actionClearPictureCache = QAction("Clear Picture Cache", self)
        self.menuFile.insertAction(self.actionClearIgnoreList, self.actionClearPictureCache)
        self.connect(self.actionClearPictureCache, SIGNAL("triggered()"), self.clearPictureCacheTriggered)
    
    def clearPictureCacheTriggered(self):
        title = "Clear Picture Cache"
        msg = "Do you really want to remove all your cached picture analysis?"
        if self._confirm(title, msg, QMessageBox.No):
            self.app.scanner.match_factory.cached_blocks.clear()
            QMessageBox.information(self, title, "Picture cache cleared.")
    