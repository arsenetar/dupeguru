#!/usr/bin/env python
# Unit Name: error_report_dialog
# Created By: Virgil Dupras
# Created On: 2009-05-23
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from PyQt4.QtCore import Qt, QUrl
from PyQt4.QtGui import QDialog, QDesktopServices

from error_report_dialog_ui import Ui_ErrorReportDialog

class ErrorReportDialog(QDialog, Ui_ErrorReportDialog):
    def __init__(self, parent, error):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        QDialog.__init__(self, parent, flags)
        self.setupUi(self)
        self.errorTextEdit.setPlainText(error)
    
    def accept(self):
        text = self.errorTextEdit.toPlainText()
        url = QUrl("mailto:support@hardcoded.net?SUBJECT=Error Report&BODY=%s" % text)
        QDesktopServices.openUrl(url)
        QDialog.accept(self)
    
