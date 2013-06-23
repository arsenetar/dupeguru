==========================================
:mod:`sqlite` - Threaded sqlite connection
==========================================

.. module:: sqlite

.. class:: ThreadedConn(dbname, autocommit)

    ``sqlite`` connections can't be used across threads. ``TheadedConn`` opens a sqlite connection in its own thread and sends it queries through a queue, making it suitable in multi-threaded environment.