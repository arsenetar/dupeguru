from objp.util import pyref, dontwrap
from cocoa.inter import PyGUIObject
from core.gui.extra_fairware_reminder import ExtraFairwareReminder

class ExtraFairwareReminderView:
    def startTimer(self): pass
    def stopTimer(self): pass
    def setButtonText_(self, text: str): pass;
    def enableButton(self): pass

class PyExtraFairwareReminder(PyGUIObject):
    def __init__(self, app: pyref):
        model = ExtraFairwareReminder(app.model)
        PyGUIObject.__init__(self, model)
    
    def start(self):
        self.model.start()
    
    def updateButton(self):
        self.model.update_button()
    
    # model --> view
    @dontwrap
    def start_timer(self):
        self.callback.startTimer()
    
    @dontwrap
    def stop_timer(self):
        self.callback.stopTimer()
    
    @dontwrap
    def enable_button(self):
        self.callback.enableButton()
    
    @dontwrap
    def set_button_text(self, text):
        self.callback.setButtonText_(text)
