==========================================
:mod:`notify` - Simple notification system
==========================================

.. module:: notify

This module is a brain-dead simple notification system involving a :class:`Broadcaster` and a :class:`Listener`. A listener can only listen to one broadcaster. A broadcaster can have multiple listeners. If the listener is connected, whenever the broadcaster calls :meth:`~Broadcaster.notify`, the method with the same name as the broadcasted message is called on the listener.

.. class:: Broadcaster

    .. method:: notify(msg)
    
        Notify all connected listeners of ``msg``. That means that each listeners will have their method with the same name as ``msg`` called.

.. class:: Listener(broadcaster)

    A listener is initialized with the broadcaster it's going to listen to. Initially, it is not connected.
    
    .. method:: connect()
    
        Connects the listener to its broadcaster.
    
    .. method:: disconnect()
        
        Disconnects the listener from its broadcaster.
    
