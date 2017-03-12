#!/usr/bin/python3
# Copyright 2017 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import sys
import os.path as op
import gc

from PyQt5.QtCore import QCoreApplication, QSettings
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication

from hscommon.trans import install_gettext_trans_under_qt
from qtlib.error_report_dialog import install_excepthook
from qtlib.util import setupQtLogging
from qt import dg_rc
from qt.platform import BASE_PATH
from core import __version__, __appname__

def main():
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName('Hardcoded Software')
    QCoreApplication.setApplicationName(__appname__)
    QCoreApplication.setApplicationVersion(__version__)
    setupQtLogging()
    settings = QSettings()
    lang = settings.value('Language')
    locale_folder = op.join(BASE_PATH, 'locale')
    install_gettext_trans_under_qt(locale_folder, lang)
    # Many strings are translated at import time, so this is why we only import after the translator
    # has been installed
    from qt.app import DupeGuru
    app.setWindowIcon(QIcon(QPixmap(":/{0}".format(DupeGuru.LOGO_NAME))))
    dgapp = DupeGuru()
    install_excepthook('https://github.com/hsoft/dupeguru/issues')
    result = app.exec()
    # I was getting weird crashes when quitting under Windows, and manually deleting main app
    # references with gc.collect() in between seems to fix the problem.
    del dgapp
    gc.collect()
    del app
    gc.collect()
    return result

if __name__ == "__main__":
    sys.exit(main())
