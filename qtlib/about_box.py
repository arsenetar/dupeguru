# Created By: Virgil Dupras
# Created On: 2009-05-09
# Copyright 2014 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QSizePolicy, QHBoxLayout, QVBoxLayout,
    QLabel, QApplication)

from hscommon.trans import trget

tr = trget('qtlib')

class AboutBox(QDialog):
    def __init__(self, parent, app, **kwargs):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.MSWindowsFixedSizeDialogHint
        super().__init__(parent, flags, **kwargs)
        self.app = app
        self._setupUi()
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
    
    def _setupUi(self):
        self.setWindowTitle(tr("About {}").format(QCoreApplication.instance().applicationName()))
        self.resize(400, 190)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.horizontalLayout = QHBoxLayout(self)
        self.logoLabel = QLabel(self)
        self.logoLabel.setPixmap(QPixmap(':/%s_big' % self.app.LOGO_NAME))
        self.horizontalLayout.addWidget(self.logoLabel)
        self.verticalLayout = QVBoxLayout()
        self.nameLabel = QLabel(self)
        font = QFont()
        font.setWeight(75)
        font.setBold(True)
        self.nameLabel.setFont(font)
        self.nameLabel.setText(QCoreApplication.instance().applicationName())
        self.verticalLayout.addWidget(self.nameLabel)
        self.versionLabel = QLabel(self)
        self.versionLabel.setText(tr("Version {}").format(QCoreApplication.instance().applicationVersion()))
        self.verticalLayout.addWidget(self.versionLabel)
        self.label_3 = QLabel(self)
        self.verticalLayout.addWidget(self.label_3)
        self.label_3.setText(tr("Copyright Hardcoded Software 2014"))
        self.label = QLabel(self)
        font = QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.verticalLayout.addWidget(self.label)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok)
        self.verticalLayout.addWidget(self.buttonBox)
        self.horizontalLayout.addLayout(self.verticalLayout)
    

if __name__ == '__main__':
    import sys
    app = QApplication([])
    QCoreApplication.setOrganizationName('Hardcoded Software')
    QCoreApplication.setApplicationName('FooApp')
    QCoreApplication.setApplicationVersion('1.2.3')
    app.LOGO_NAME = ''
    dialog = AboutBox(None, app)
    dialog.show()
    sys.exit(app.exec_())
