from objp.util import dontwrap
from cocoa.inter2 import PyGUIObject2

class ExtraFairwareReminderView:
    def startTimer(self): pass
    def stopTimer(self): pass
    def setButtonText_(self, text: str): pass;
    def enableButton(self): pass

class PyExtraFairwareReminder(PyGUIObject2):
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
