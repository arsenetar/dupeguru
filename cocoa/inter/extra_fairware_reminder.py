from cocoa.inter2 import PyGUIObject

class PyExtraFairwareReminder(PyGUIObject):
    def start(self):
        self.model.start()
    
    def updateButton(self):
        self.model.update_button()
    
    # model --> view
    def start_timer(self):
        self.callback.startTimer()
    
    def stop_timer(self):
        self.callback.stopTimer()
    
    def enable_button(self):
        self.callback.enableButton()
    
    def set_button_text(self, text):
        self.callback.setButtonText_(text)
