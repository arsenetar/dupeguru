#!/usr/bin/env python
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import sys

from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import QApplication, QIcon, QPixmap

import base.dg_rc

from app import DupeGuru

# This is a workaround for a pyinstaller problem where compiled dupeguru can't read tiff files
from PIL import TiffImagePlugin, TiffTags

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(QPixmap(":/logo_pe")))
    QCoreApplication.setOrganizationName('Hardcoded Software')
    QCoreApplication.setApplicationName(DupeGuru.NAME)
    QCoreApplication.setApplicationVersion(DupeGuru.VERSION)
    dgapp = DupeGuru()
    sys.exit(app.exec_())