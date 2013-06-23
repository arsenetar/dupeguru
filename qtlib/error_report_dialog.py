# Created By: Virgil Dupras
# Created On: 2009-05-23
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import traceback
import sys
import os

from PyQt4.QtCore import Qt, QUrl, QCoreApplication, QSize
from PyQt4.QtGui import (QDialog, QDesktopServices, QVBoxLayout, QHBoxLayout, QLabel,
    QPlainTextEdit, QPushButton, QApplication)

from hscommon.trans import trget
from .util import horizontalSpacer

tr = trget('qtlib')

class ErrorReportDialog(QDialog):
    def __init__(self, parent, error):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        QDialog.__init__(self, parent, flags)
        self._setupUi()
        name = QCoreApplication.applicationName()
        version = QCoreApplication.applicationVersion()
        errorText = "Application Name: {0}\nVersion: {1}\n\n{2}".format(name, version, error)
        # Under windows, we end up with an error report without linesep if we don't mangle it
        errorText = errorText.replace('\n', os.linesep)
        self.errorTextEdit.setPlainText(errorText)
        
        self.sendButton.clicked.connect(self.accept)
        self.dontSendButton.clicked.connect(self.reject)
    
    def _setupUi(self):
        self.setWindowTitle(tr("Error Report"))
        self.resize(553, 349)
        self.verticalLayout = QVBoxLayout(self)
        self.label = QLabel(self)
        self.label.setText(tr("Something went wrong. Would you like to send the error report to Hardcoded Software?"))
        self.label.setWordWrap(True)
        self.verticalLayout.addWidget(self.label)
        self.errorTextEdit = QPlainTextEdit(self)
        self.errorTextEdit.setReadOnly(True)
        self.verticalLayout.addWidget(self.errorTextEdit)
        msg = tr("Although the application should continue to run after this error, it may be in an "
            "instable state, so it is recommended that you restart the application.")
        self.label2 = QLabel(msg)
        self.label2.setWordWrap(True)
        self.verticalLayout.addWidget(self.label2)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.addItem(horizontalSpacer())
        self.dontSendButton = QPushButton(self)
        self.dontSendButton.setText(tr("Don\'t Send"))
        self.dontSendButton.setMinimumSize(QSize(110, 0))
        self.horizontalLayout.addWidget(self.dontSendButton)
        self.sendButton = QPushButton(self)
        self.sendButton.setText(tr("Send"))
        self.sendButton.setMinimumSize(QSize(110, 0))
        self.sendButton.setDefault(True)
        self.horizontalLayout.addWidget(self.sendButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
    
    def accept(self):
        text = self.errorTextEdit.toPlainText()
        url = QUrl("mailto:support@hardcoded.net?SUBJECT=Error Report&BODY=%s" % text)
        QDesktopServices.openUrl(url)
        QDialog.accept(self)
    

def install_excepthook():
    def my_excepthook(exctype, value, tb):
        s = ''.join(traceback.format_exception(exctype, value, tb))
        dialog = ErrorReportDialog(None, s)
        dialog.exec_()
    
    sys.excepthook = my_excepthook

if __name__ == '__main__':
    app = QApplication([])
    QCoreApplication.setOrganizationName('Hardcoded Software')
    QCoreApplication.setApplicationName('FooApp')
    QCoreApplication.setApplicationVersion('1.2.3')
    dialog = ErrorReportDialog(None, 'some traceback')
    dialog.show()
    sys.exit(app.exec_())