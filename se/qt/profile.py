import sys
import cProfile
import pstats

from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import QApplication

if sys.platform == 'win32':
    from app_win import DupeGuru
else:
    from app import DupeGuru

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName('Hardcoded Software')
    QCoreApplication.setApplicationName('dupeGuru')
    dgapp = DupeGuru()
    cProfile.run('app.exec_()', '/tmp/prof')
    p = pstats.Stats('/tmp/prof')
    p.sort_stats('time').print_stats()