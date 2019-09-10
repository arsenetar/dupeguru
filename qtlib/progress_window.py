# Copyright 2016 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QProgressDialog

class ProgressWindow:
    def __init__(self, parent, model):
        self._window = None
        self.parent = parent
        self.model = model
        model.view = self
        # We don't have access to QProgressDialog's labels directly, so we se the model label's view
        # to self and we'll refresh them together.
        self.model.jobdesc_textfield.view = self
        self.model.progressdesc_textfield.view = self

    # --- Callbacks
    def refresh(self): # Labels
        if self._window is not None:
            self._window.setWindowTitle(self.model.jobdesc_textfield.text)
            self._window.setLabelText(self.model.progressdesc_textfield.text)

    def set_progress(self, last_progress):
        if self._window is not None:
            self._window.setValue(last_progress)

    def show(self):
        flags = Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
        self._window = QProgressDialog('', "Cancel", 0, 100, self.parent, flags)
        self._window.setModal(True)
        self._window.setAutoReset(False)
        self._window.setAutoClose(False)
        self._timer = QTimer(self._window)
        self._timer.timeout.connect(self.model.pulse)
        self._window.show()
        self._window.canceled.connect(self.model.cancel)
        self._timer.start(500)

    def close(self):
        # it seems it is possible for close to be called without a corresponding
        # show, only perform a close if there is a window to close
        if self._window is not None:
            self._timer.stop()
            del self._timer
            # For some weird reason, canceled() signal is sent upon close, whether the user canceled
            # or not. If we don't want a false cancellation, we have to disconnect it.
            self._window.canceled.disconnect()
            self._window.close()
            self._window.setParent(None)
            self._window = None

