#!/usr/bin/env python3
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys
import sip
sip.setapi('QVariant', 1)

from PyQt4.QtCore import QCoreApplication, QSettings
from PyQt4.QtGui import QApplication, QIcon, QPixmap

from hscommon.plat import ISWINDOWS
from hscommon.trans import install_gettext_trans_under_qt
from qtlib.error_report_dialog import install_excepthook
from qt.base import dg_rc
from core_{{edition}} import __version__, __appname__

if ISWINDOWS:
    import qt.base.cxfreeze_fix

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName('Hardcoded Software')
    QCoreApplication.setApplicationName(__appname__)
    QCoreApplication.setApplicationVersion(__version__)
    settings = QSettings()
    lang = settings.value('Language').toString()
    install_gettext_trans_under_qt(lang)
    # Many strings are translated at import time, so this is why we only import after the translator
    # has been installed
    from qt.{{edition}}.app import DupeGuru
    app.setWindowIcon(QIcon(QPixmap(":/{0}".format(DupeGuru.LOGO_NAME))))
    dgapp = DupeGuru()
    install_excepthook()
    sys.exit(app.exec_())
