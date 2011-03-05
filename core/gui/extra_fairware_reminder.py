# Created By: Virgil Dupras
# Created On: 2011-03-04
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import time

from hscommon.trans import tr
from .base import GUIObject

class ExtraFairwareReminder(GUIObject):
    def start(self):
        self.start_time = time.time()
        self.view.start_timer()
    
    def update_button(self):
        elapsed = time.time() - self.start_time
        remaining = 60 - round(elapsed)
        if remaining > 0:
            text = tr("Continue ({})").format(remaining)
        else:
            text = tr("Continue")
            self.view.enable_button()
            self.view.stop_timer()
        self.view.set_button_text(text)
    
    