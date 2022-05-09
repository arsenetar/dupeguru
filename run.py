#!/usr/bin/python3
# Copyright 2017 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import sys
import os.path as op
import gc

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication

from hscommon.trans import install_gettext_trans_under_qt
from qt.error_report_dialog import install_excepthook
from qt.util import setup_qt_logging, create_qsettings
from qt import dg_rc  # noqa: F401
from qt.platform import BASE_PATH
from core import __version__, __appname__

# SIGQUIT is not defined on Windows
if sys.platform == "win32":
    from signal import signal, SIGINT, SIGTERM

    SIGQUIT = SIGTERM
else:
    from signal import signal, SIGINT, SIGTERM, SIGQUIT

global dgapp
dgapp = None


def signal_handler(sig, frame):
    global dgapp
    if dgapp is None:
        return
    if sig in (SIGINT, SIGTERM, SIGQUIT):
        dgapp.SIGTERM.emit()


def setup_signals():
    signal(SIGINT, signal_handler)
    signal(SIGTERM, signal_handler)
    signal(SIGQUIT, signal_handler)


def main():
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName("Hardcoded Software")
    QCoreApplication.setApplicationName(__appname__)
    QCoreApplication.setApplicationVersion(__version__)
    setup_qt_logging()
    settings = create_qsettings()
    lang = settings.value("Language")
    locale_folder = op.join(BASE_PATH, "locale")
    install_gettext_trans_under_qt(locale_folder, lang)
    # Handle OS signals
    setup_signals()
    # Let the Python interpreter runs every 500ms to handle signals.  This is
    # required because Python cannot handle signals while the Qt event loop is
    # running.
    from PyQt5.QtCore import QTimer

    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)
    # Many strings are translated at import time, so this is why we only import after the translator
    # has been installed
    from qt.app import DupeGuru

    app.setWindowIcon(QIcon(QPixmap(f":/{DupeGuru.LOGO_NAME}")))
    global dgapp
    dgapp = DupeGuru()
    install_excepthook("https://github.com/arsenetar/dupeguru/issues")
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
