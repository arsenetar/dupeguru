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

from PyQt6.QtCore import Qt, QCoreApplication, QSize
from PyQt6.QtWidgets import (
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
        flags = Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowSystemMenuHint
        super().__init__(parent, flags, **kwargs)
        self._setupUi()
        name = QCoreApplication.applicationName()
        version = QCoreApplication.applicationVersion()
        error_text = "Application Name: {}\nVersion: {}\nPython: {}\nOperating System: {}\n\n{}".format(
            name, version, platform.python_version(), platform.platform(), error
        )
        # Under windows, we end up with an error report without linesep if we don't mangle it
        error_text = error_text.replace("\n", os.linesep)
        self.error_text_edit.setPlainText(error_text)
        self.github_url = github_url

    def _setupUi(self):
        self.setWindowTitle(tr("Error Report"))
        self.resize(553, 349)
        main_layout = QVBoxLayout(self)

        title_label = QLabel(self)
        title_label.setText(tr("Something went wrong. How about reporting the error?"))
        title_label.setWordWrap(True)
        main_layout.addWidget(title_label)

        self.error_text_edit = QPlainTextEdit(self)
        self.error_text_edit.setReadOnly(True)
        main_layout.addWidget(self.error_text_edit)

        msg = tr(
            "Error reports should be reported as Github issues. You can copy the error traceback "
            "above and paste it in a new issue.\n\nPlease make sure to run a search for any already "
            "existing issues beforehand. Also make sure to test the very latest version available from the repository, "
            "since the bug you are experiencing might have already been patched.\n\n"
            "What usually really helps is if you add a description of how you got the error. Thanks!"
            "\n\n"
            "Although the application should continue to run after this error, it may be in an "
            "unstable state, so it is recommended that you restart the application."
        )
        instructions_label = QLabel(msg)
        instructions_label.setWordWrap(True)
        main_layout.addWidget(instructions_label)

        button_layout = QHBoxLayout()
        button_layout.addItem(horizontal_spacer())

        close_button = QPushButton(self)
        close_button.setText(tr("Close"))
        close_button.setMinimumSize(QSize(110, 0))
        button_layout.addWidget(close_button)

        report_button = QPushButton(self)
        report_button.setText(tr("Go to Github"))
        report_button.setMinimumSize(QSize(110, 0))
        report_button.setDefault(True)
        button_layout.addWidget(report_button)

        main_layout.addLayout(button_layout)

        report_button.clicked.connect(self.goToGithub)
        close_button.clicked.connect(self.reject)

    def goToGithub(self):
        open_url(self.github_url)


def install_excepthook(github_url):
    def my_excepthook(exctype, value, tb):
        s = "".join(traceback.format_exception(exctype, value, tb))
        dialog = ErrorReportDialog(None, github_url, s)
        dialog.exec()

    sys.excepthook = my_excepthook
