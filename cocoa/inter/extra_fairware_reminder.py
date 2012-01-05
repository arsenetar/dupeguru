from cocoa.inter import PyGUIObject

from core.gui.extra_fairware_reminder import ExtraFairwareReminder

class PyExtraFairwareReminder(PyGUIObject):
    py_class = ExtraFairwareReminder
    
    def start(self):
        self.py.start()
    
    def updateButton(self):
        self.py.update_button()
    
    # model --> view
    def start_timer(self):
        self.cocoa.startTimer()
    
    def stop_timer(self):
        self.cocoa.stopTimer()
    
    def enable_button(self):
        self.cocoa.enableButton()
    
    def set_button_text(self, text):
        self.cocoa.setButtonText_(text)