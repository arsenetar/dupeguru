# Created On: 2012/01/23
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

class TextField:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.model.view = self
        # Make TextField also work for QLabel, which doesn't allow editing
        if hasattr(self.view, 'editingFinished'):
            self.view.editingFinished.connect(self.editingFinished)
    
    def editingFinished(self):
        self.model.text = self.view.text()
    
    # model --> view
    def refresh(self):
        self.view.setText(self.model.text)
    
