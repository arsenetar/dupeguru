# Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

"""Very simple inter-object notification system.

This module is a brain-dead simple notification system involving a :class:`Broadcaster` and a
:class:`Listener`. A listener can only listen to one broadcaster. A broadcaster can have multiple
listeners. If the listener is connected, whenever the broadcaster calls :meth:`~Broadcaster.notify`,
the method with the same name as the broadcasted message is called on the listener.
"""

from collections import defaultdict

class Broadcaster:
    """Broadcasts messages that are received by all listeners.
    """
    def __init__(self):
        self.listeners = set()
    
    def add_listener(self, listener):
        self.listeners.add(listener)
    
    def notify(self, msg):
        """Notify all connected listeners of ``msg``.
        
        That means that each listeners will have their method with the same name as ``msg`` called.
        """
        for listener in self.listeners.copy(): # listeners can change during iteration
            if listener in self.listeners: # disconnected during notification
                listener.dispatch(msg)
    
    def remove_listener(self, listener):
        self.listeners.discard(listener)
    

class Listener:
    """A listener is initialized with the broadcaster it's going to listen to. Initially, it is not connected.
    """
    def __init__(self, broadcaster):
        self.broadcaster = broadcaster
        self._bound_notifications = defaultdict(list)
    
    def bind_messages(self, messages, func):
        """Binds multiple message to the same function.
        
        Often, we perform the same thing on multiple messages. Instead of having the same function
        repeated again and agin in our class, we can use this method to bind multiple messages to
        the same function.
        """
        for message in messages:
            self._bound_notifications[message].append(func)
    
    def connect(self):
        """Connects the listener to its broadcaster.
        """
        self.broadcaster.add_listener(self)
    
    def disconnect(self):
        """Disconnects the listener from its broadcaster.
        """
        self.broadcaster.remove_listener(self)
    
    def dispatch(self, msg):
        if msg in self._bound_notifications:
            for func in self._bound_notifications[msg]:
                func()
        if hasattr(self, msg):
            method = getattr(self, msg)
            method()
    

class Repeater(Broadcaster, Listener):
    REPEATED_NOTIFICATIONS = None
    
    def __init__(self, broadcaster):
        Broadcaster.__init__(self)
        Listener.__init__(self, broadcaster)
    
    def _repeat_message(self, msg):
        if not self.REPEATED_NOTIFICATIONS or msg in self.REPEATED_NOTIFICATIONS:
            self.notify(msg)
    
    def dispatch(self, msg):
        Listener.dispatch(self, msg)
        self._repeat_message(msg)
    
