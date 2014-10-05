# Created By: Virgil Dupras
# Created On: 2009-09-14
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import pyqtSignal, Qt, QTimer
from PyQt4.QtGui import QProgressDialog

from . import job, performer

class Progress(QProgressDialog, performer.ThreadedJobPerformer):
    finished = pyqtSignal(['QString'])
    
    def __init__(self, parent):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        QProgressDialog.__init__(self, '', "Cancel", 0, 100, parent, flags)
        self.setModal(True)
        self.setAutoReset(False)
        self.setAutoClose(False)
        self._timer = QTimer()
        self._jobid = ''
        self._timer.timeout.connect(self.updateProgress)
    
    def updateProgress(self):
        # the values might change before setValue happens
        last_progress = self.last_progress
        last_desc = self.last_desc
        if not self._job_running or last_progress is None:
            self._timer.stop()
            self.close()
            if not self.job_cancelled:
                self.finished.emit(self._jobid)
            return
        if self.wasCanceled():
            self.job_cancelled = True
            return
        if last_desc:
            self.setLabelText(last_desc)
        self.setValue(last_progress)
    
    def run(self, jobid, title, target, args=()):
        self._jobid = jobid
        self.reset()
        self.setLabelText('')
        self.run_threaded(target, args)
        self.setWindowTitle(title)
        self.show()
        self._timer.start(500)
    
