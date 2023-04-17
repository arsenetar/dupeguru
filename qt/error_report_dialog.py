# Created By: Virgil Dupras
# Created On: 2009-05-23
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import traceback
import sys
import os
import platform

from PyQt5.QtCore import Qt, QCoreApplication, QSize
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
)

from hscommon.trans import trget
from hscommon.desktop import open_url
from qt.util import horizontal_spacer

tr = trget("ui")


class ErrorReportDialog(QDialog):
    def __init__(self, parent, github_url, error, **kwargs):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        super().__init__(parent, flags, **kwargs)
        self._setupUi()
        name = QCoreApplication.applicationName()
        version = QCoreApplication.applicationVersion()
        error_text = "Application Name: {}\nVersion: {}\nPython: {}\nOperating System: {}\n\n{}".format(
            name, version, platform.python_version(), platform.platform(), error
        )
        # Under windows, we end up with an error report without linesep if we don't mangle it
        error_text = error_text.replace("\n", os.linesep)
        self.errorTextEdit.setPlainText(error_text)
        self.github_url = github_url

        self.sendButton.clicked.connect(self.goToGitHub)
        self.dontSendButton.clicked.connect(self.reject)

    def _setupUi(self):
        self.setWindowTitle(tr("Error Report"))
        self.resize(553, 349)
        self.verticalLayout = QVBoxLayout(self)
        self.label = QLabel(self)
        self.label.setText(tr("Something went wrong. How about reporting the error?"))
        self.label.setWordWrap(True)
        self.verticalLayout.addWidget(self.label)
        self.errorTextEdit = QPlainTextEdit(self)
        self.errorTextEdit.setReadOnly(True)
        self.verticalLayout.addWidget(self.errorTextEdit)
        msg = tr(
            "Error reports should be reported as GitHub issues. You can copy the error traceback "
            "above and paste it in a new issue.\n\nPlease make sure to run a search for any already "
            "existing issues beforehand. Also make sure to test the very latest version available from the repository, "
            "since the bug you are experiencing might have already been patched.\n\n"
            "What usually really helps is if you add a description of how you got the error. Thanks!"
            "\n\n"
            "Although the application should continue to run after this error, it may be in an "
            "unstable state, so it is recommended that you restart the application."
        )
        self.label2 = QLabel(msg)
        self.label2.setWordWrap(True)
        self.verticalLayout.addWidget(self.label2)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.addItem(horizontal_spacer())
        self.dontSendButton = QPushButton(self)
        self.dontSendButton.setText(tr("Close"))
        self.dontSendButton.setMinimumSize(QSize(110, 0))
        self.horizontalLayout.addWidget(self.dontSendButton)
        self.sendButton = QPushButton(self)
        self.sendButton.setText(tr("Go to GitHub"))
        self.sendButton.setMinimumSize(QSize(110, 0))
        self.sendButton.setDefault(True)
        self.horizontalLayout.addWidget(self.sendButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

    def goToGitHub(self):
        open_url(self.github_url)


def install_excepthook(github_url):
    def my_excepthook(exctype, value, tb):
        s = "".join(traceback.format_exception(exctype, value, tb))
        dialog = ErrorReportDialog(None, github_url, s)
        dialog.exec_()

    sys.excepthook = my_excepthook
