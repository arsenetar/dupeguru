# Created By: Virgil Dupras
# Created On: 2011/09/09
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

def noop(*args, **kwargs):
    pass

class NoopGUI:
    def __getattr__(self, func_name):
        return noop

class GUIObject:
    """Cross-toolkit "model" representation of a GUI layer object.
    
    A ``GUIObject`` is a cross-toolkit "model" representation of a GUI layer object, for example, a
    table. It acts as a cross-toolkit interface to what we call here a :attr:`view`. That
    view is a toolkit-specific controller to the actual view (an ``NSTableView``, a ``QTableView``,
    etc.). In our GUIObject, we need a reference to that toolkit-specific controller because some
    actions have effects on it (for example, prompting it to refresh its data). The ``GUIObject``
    is typically instantiated before its :attr:`view`, that is why we set it to ``None`` on init.
    However, the GUI layer is supposed to set the view as soon as its toolkit-specific controller is
    instantiated.

    When you subclass ``GUIObject``, you will likely want to update its view on instantiation. That
    is why we call ``self.view.refresh()`` in :meth:`_view_updated`. If you need another type of
    action on view instantiation, just override the method.
    """
    def __init__(self):
        self._view = None
    
    def _view_updated(self):
        """(Virtual) Called after :attr:`view` has been set.
        
        Doing nothing by default, this method is called after :attr:`view` has been set (it isn't
        called when it's unset, however). Use this for initialization code that requires a view
        (which is often the whole of the initialization code).
        """
    
    def has_view(self):
        return (self._view is not None) and (not isinstance(self._view, NoopGUI))
    
    @property
    def view(self):
        """A reference to our toolkit-specific view controller.
        
        *view answering to GUIObject sublass's view protocol*. *get/set*
        
        This view starts as ``None`` and has to be set "manually". There's two times at which we set
        the view property: On initialization, where we set the view that we'll use for our lifetime,
        and just before the view is deallocated. We need to unset our view at that time to avoid
        calls to a deallocated instance (which means a crash).
        
        To unset our view, we simple assign it to ``None``.
        """
        return self._view
    
    @view.setter
    def view(self, value):
        if self._view is None:
            # Initial view assignment
            if value is None:
                return 
            self._view = value
            self._view_updated()
        else:
            assert value is None
            # Instead of None, we put a NoopGUI() there to avoid rogue view callback raising an
            # exception.
            self._view = NoopGUI()
    
