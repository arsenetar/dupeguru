# Created By: Virgil Dupras
# Created On: 2009-05-10
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys

from PyQt4.QtCore import Qt, QCoreApplication
from PyQt4.QtGui import (QDialog, QApplication, QVBoxLayout, QHBoxLayout, QLabel,
    QFont, QSpacerItem, QSizePolicy, QPushButton)

from hscommon.plat import ISLINUX
from hscommon.trans import trget

tr = trget('qtlib')

class RegDemoDialog(QDialog):
    def __init__(self, parent, reg, prompt):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        QDialog.__init__(self, parent, flags)
        self.reg = reg
        self._setupUi()
        self.descLabel.setText(prompt)
        
        self.enterCodeButton.clicked.connect(self.enterCodeClicked)
        self.buyButton.clicked.connect(self.buyClicked)
        self.tryButton.clicked.connect(self.accept)
        self.moreInfoButton.clicked.connect(self.moreInfoClicked)
    
    def _setupUi(self):
        appname = QCoreApplication.instance().applicationName()
        title = tr("$appname is Fairware")
        title = title.replace('$appname', appname)
        self.setWindowTitle(title)
        # Workaround for bug at http://bugreports.qt.nokia.com/browse/QTBUG-8212
        dlg_height = 370 if ISLINUX else 240
        self.resize(400, dlg_height)
        self.verticalLayout = QVBoxLayout(self)
        self.descLabel = QLabel(self)        
        self.descLabel.setWordWrap(True)
        self.verticalLayout.addWidget(self.descLabel)
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QHBoxLayout()
        self.tryButton = QPushButton(self)
        self.tryButton.setText(tr("Try"))
        self.horizontalLayout.addWidget(self.tryButton)
        self.enterCodeButton = QPushButton(self)
        self.enterCodeButton.setText(tr("Enter Key"))
        self.horizontalLayout.addWidget(self.enterCodeButton)
        self.buyButton = QPushButton(self)
        self.buyButton.setText(tr("Buy"))
        self.horizontalLayout.addWidget(self.buyButton)
        self.moreInfoButton = QPushButton(tr("Fairware?"))
        self.horizontalLayout.addWidget(self.moreInfoButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
    
    #--- Events
    def enterCodeClicked(self):
        if self.reg.ask_for_code():
            self.accept()
    
    def buyClicked(self):
        self.reg.app.buy()
    
    def moreInfoClicked(self):
        self.reg.app.about_fairware()
    

if __name__ == '__main__':
    app = QApplication([])
    app.unpaid_hours = 42.4
    class FakeReg:
        app = app
    dialog = RegDemoDialog(None, FakeReg(), "foo bar baz")
    dialog.show()
    sys.exit(app.exec_())
