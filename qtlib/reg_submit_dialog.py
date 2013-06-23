# Created By: Virgil Dupras
# Created On: 2009-05-09
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys

from PyQt4.QtCore import Qt, QCoreApplication
from PyQt4.QtGui import (QDialog, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QFormLayout,
    QLayout, QLineEdit, QPushButton, QSpacerItem, QSizePolicy)

from hscommon.trans import trget

tr = trget('qtlib')

class RegSubmitDialog(QDialog):
    def __init__(self, parent, reg):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        QDialog.__init__(self, parent, flags)
        self._setupUi()
        self.reg = reg
        
        self.submitButton.clicked.connect(self.submitClicked)
        self.contributeButton.clicked.connect(self.contributeClicked)
        self.cancelButton.clicked.connect(self.reject)
    
    def _setupUi(self):
        self.setWindowTitle(tr("Enter your registration key"))
        self.resize(365, 126)
        self.verticalLayout = QVBoxLayout(self)
        self.promptLabel = QLabel(self)
        appname = str(QCoreApplication.instance().applicationName())
        prompt = tr("Type the key you received when you contributed to $appname, as well as the "
            "e-mail used as a reference for the purchase.").replace('$appname', appname)
        self.promptLabel.setText(prompt)
        self.promptLabel.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.promptLabel.setWordWrap(True)
        self.verticalLayout.addWidget(self.promptLabel)
        self.formLayout = QFormLayout()
        self.formLayout.setSizeConstraint(QLayout.SetNoConstraint)
        self.formLayout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setLabelAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.formLayout.setFormAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.label2 = QLabel(self)
        self.label2.setText(tr("Registration key:"))
        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label2)
        self.label3 = QLabel(self)
        self.label3.setText(tr("Registered e-mail:"))
        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label3)
        self.codeEdit = QLineEdit(self)
        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.codeEdit)
        self.emailEdit = QLineEdit(self)
        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.emailEdit)
        self.verticalLayout.addLayout(self.formLayout)
        self.horizontalLayout = QHBoxLayout()
        self.contributeButton = QPushButton(self)
        self.contributeButton.setText(tr("Contribute"))
        self.contributeButton.setAutoDefault(False)
        self.horizontalLayout.addWidget(self.contributeButton)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cancelButton = QPushButton(self)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cancelButton.sizePolicy().hasHeightForWidth())
        self.cancelButton.setSizePolicy(sizePolicy)
        self.cancelButton.setText(tr("Cancel"))
        self.cancelButton.setAutoDefault(False)
        self.horizontalLayout.addWidget(self.cancelButton)
        self.submitButton = QPushButton(self)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.submitButton.sizePolicy().hasHeightForWidth())
        self.submitButton.setSizePolicy(sizePolicy)
        self.submitButton.setText(tr("Submit"))
        self.submitButton.setAutoDefault(False)
        self.submitButton.setDefault(True)
        self.horizontalLayout.addWidget(self.submitButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
    
    #--- Events
    def contributeClicked(self):
        self.reg.app.contribute()
    
    def submitClicked(self):
        code = self.codeEdit.text()
        email = self.emailEdit.text()
        if self.reg.app.set_registration(code, email, False):
            self.accept()
    

if __name__ == '__main__':
    app = QApplication([])
    validate = lambda *args: True
    dialog = RegSubmitDialog(None, validate)
    dialog.show()
    sys.exit(app.exec_())
