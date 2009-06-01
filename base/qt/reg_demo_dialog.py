#!/usr/bin/env python
# Unit Name: reg_demo_dialog
# Created By: Virgil Dupras
# Created On: 2009-05-10
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from PyQt4.QtCore import SIGNAL, Qt, QUrl, QCoreApplication
from PyQt4.QtGui import QDialog, QMessageBox, QDesktopServices

from reg_demo_dialog_ui import Ui_RegDemoDialog

class RegDemoDialog(QDialog, Ui_RegDemoDialog):
    def __init__(self, parent, reg):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        QDialog.__init__(self, parent, flags)
        self.reg = reg
        self._setupUi()
        
        self.connect(self.enterCodeButton, SIGNAL('clicked()'), self.enterCodeClicked)
        self.connect(self.purchaseButton, SIGNAL('clicked()'), self.purchaseClicked)
    
    def _setupUi(self):
        self.setupUi(self)
        # Stuff that can't be setup in the Designer
        appname = QCoreApplication.instance().applicationName()
        title = self.windowTitle()
        title = title.replace('$appname', appname)
        self.setWindowTitle(title)
        title = self.titleLabel.text()
        title = title.replace('$appname', appname)
        self.titleLabel.setText(title)
        desc = self.demoDescLabel.text()
        desc = desc.replace('$appname', appname)
        self.demoDescLabel.setText(desc)
    
    #--- Events
    def enterCodeClicked(self):
        if self.reg.ask_for_code():
            self.accept()
    
    def purchaseClicked(self):
        url = QUrl('http://www.hardcoded.net/purchase.htm')
        QDesktopServices.openUrl(url)
    
