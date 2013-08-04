# Created By: Virgil Dupras
# Created On: 2013-07-01
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QProgressDialog

class ProgressWindow(QProgressDialog):
    def __init__(self, parent, model):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        QProgressDialog.__init__(self, '', "Cancel", 0, 100, parent, flags)
        self.model = model
        model.view = self
        # We don't have access to QProgressDialog's labels directly, so we se the model label's view
        # to self and we'll refresh them together.
        self.model.jobdesc_textfield.view = self
        self.model.progressdesc_textfield.view = self
        self.setModal(True)
        self.setAutoReset(False)
        self.setAutoClose(False)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.model.pulse)
    
    # --- Callbacks
    def refresh(self): # Labels
        self.setWindowTitle(self.model.jobdesc_textfield.text)
        self.setLabelText(self.model.progressdesc_textfield.text)
    
    def set_progress(self, last_progress):
        self.setValue(last_progress)
    
    def show(self):
        self.reset()
        QProgressDialog.show(self)
        self.canceled.connect(self.model.cancel)
        self._timer.start(500)
    
    def close(self):
        self._timer.stop()
        # For some weird reason, canceled() signal is sent upon close, whether the user canceled
        # or not. If we don't want a false cancellation, we have to disconnect it.
        self.canceled.disconnect()
        QProgressDialog.close(self)
    
