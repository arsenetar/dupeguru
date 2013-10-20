# Created On: 2010-06-02
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QRadioButton

from .util import horizontalSpacer

class RadioBox(QWidget):
    def __init__(self, parent=None, items=None, spread=True, **kwargs):
        # If spread is False, insert a spacer in the layout so that the items don't use all the
        # space they're given but rather align left.
        if items is None:
            items = []
        super().__init__(parent, **kwargs)
        self._buttons = []
        self._labels = items
        self._selected_index = 0
        self._spacer = horizontalSpacer() if not spread else None
        self._layout = QHBoxLayout(self)
        self._update_buttons()
    
    #--- Private
    def _update_buttons(self):
        if self._spacer is not None:
            self._layout.removeItem(self._spacer)
        to_remove = self._buttons[len(self._labels):]
        for button in to_remove:
            self._layout.removeWidget(button)
            button.setParent(None)
        del self._buttons[len(self._labels):]
        to_add = self._labels[len(self._buttons):]
        for _ in to_add:
            button = QRadioButton(self)
            self._buttons.append(button)
            self._layout.addWidget(button)
            button.toggled.connect(self.buttonToggled)
        if self._spacer is not None:
            self._layout.addItem(self._spacer)
        if not self._buttons:
            return
        for button, label in zip(self._buttons, self._labels):
            button.setText(label)
        self._update_selection()
    
    def _update_selection(self):
        self._selected_index = max(0, min(self._selected_index, len(self._buttons)-1))
        selected = self._buttons[self._selected_index]
        selected.setChecked(True)
    
    #--- Event Handlers
    def buttonToggled(self):
        for i, button in enumerate(self._buttons):
            if button.isChecked():
                self._selected_index = i
                self.itemSelected.emit(i)
                break
    
    #--- Signals
    itemSelected = pyqtSignal(int)
    
    #--- Properties
    @property
    def buttons(self):
        return self._buttons[:]
    
    @property
    def items(self):
        return self._labels[:]
    
    @items.setter
    def items(self, value):
        self._labels = value
        self._update_buttons()
    
    @property
    def selected_index(self):
        return self._selected_index
    
    @selected_index.setter
    def selected_index(self, value):
        self._selected_index = value
        self._update_selection()
    
