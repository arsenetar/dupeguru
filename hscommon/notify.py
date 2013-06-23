# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from collections import defaultdict

class Broadcaster:
    def __init__(self):
        self.listeners = set()
    
    def add_listener(self, listener):
        self.listeners.add(listener)
    
    def notify(self, msg):
        for listener in self.listeners.copy(): # listeners can change during iteration
            if listener in self.listeners: # disconnected during notification
                listener.dispatch(msg)
    
    def remove_listener(self, listener):
        self.listeners.discard(listener)
    

class Listener:
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
        self.broadcaster.add_listener(self)
    
    def disconnect(self):
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
    
