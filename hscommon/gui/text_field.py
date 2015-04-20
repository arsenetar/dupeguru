# Created On: 2012/01/23
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from .base import GUIObject
from ..util import nonone

class TextFieldView:
    """Expected interface for :class:`TextField`'s view.
    
    *Not actually used in the code. For documentation purposes only.*
    
    Our view is expected to sync with :attr:`TextField.text` "both ways", that is, update the
    model's text when the user types something, but also update the text field when :meth:`refresh`
    is called.
    """
    def refresh(self):
        """Refreshes the contents of the input widget.
        
        Ensures that the contents of the input widget is actually :attr:`TextField.text`.
        """

class TextField(GUIObject):
    """Cross-toolkit text field.
    
    Represents a UI element allowing the user to input a text value. Its main attribute is
    :attr:`text` which acts as the store of the said value.
    
    When our model value isn't a string, we have a built-in parsing/formatting mechanism allowing
    us to directly retrieve/set our non-string value through :attr:`value`.
    
    Subclasses :class:`.GUIObject`. Expected view: :class:`TextFieldView`.
    """
    def __init__(self):
        GUIObject.__init__(self)
        self._text = ''
        self._value = None
    
    #--- Virtual
    def _parse(self, text):
        """(Virtual) Parses ``text`` to put into :attr:`value`.
        
        Returns the parsed version of ``text``. Called whenever :attr:`text` changes.
        """
        return text
    
    def _format(self, value):
        """(Virtual) Formats ``value`` to put into :attr:`text`.
        
        Returns the formatted version of ``value``. Called whenever :attr:`value` changes.
        """
        return value
    
    def _update(self, newvalue):
        """(Virtual) Called whenever we have a new value.
        
        Whenever our text/value store changes to a new value (different from the old one), this
        method is called. By default, it does nothing but you can override it if you want.
        """
    
    #--- Override
    def _view_updated(self):
        self.view.refresh()
    
    #--- Public
    def refresh(self):
        """Triggers a view :meth:`~TextFieldView.refresh`.
        """
        self.view.refresh()
    
    @property
    def text(self):
        """The text that is currently displayed in the widget.
        
        *str*. *get/set*.
        
        This property can be set. When it is, :meth:`refresh` is called and the view is synced with
        our value. Always in sync with :attr:`value`.
        """
        return self._text
    
    @text.setter
    def text(self, newtext):
        self.value = self._parse(nonone(newtext, ''))
    
    @property
    def value(self):
        """The "parsed" representation of :attr:`text`.
        
        *arbitrary type*. *get/set*.
        
        By default, it's a mirror of :attr:`text`, but a subclass can override :meth:`_parse` and
        :meth:`_format` to have anything else. Always in sync with :attr:`text`.
        """
        return self._value
    
    @value.setter
    def value(self, newvalue):
        if newvalue == self._value:
            return
        self._value = newvalue
        self._text = self._format(newvalue)
        self._update(self._value)
        self.refresh()
    
