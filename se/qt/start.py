import sys

from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import QApplication, QIcon, QPixmap

import base.dg_rc

if sys.platform == 'win32':
    from app_win import DupeGuru
else:
    from app import DupeGuru

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(QPixmap(":/logo_se")))
    QCoreApplication.setOrganizationName('Hardcoded Software')
    QCoreApplication.setApplicationName(DupeGuru.NAME)
    QCoreApplication.setApplicationVersion(DupeGuru.VERSION)
    dgapp = DupeGuru()
    sys.exit(app.exec_())