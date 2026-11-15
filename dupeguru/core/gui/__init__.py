"""
Meta GUI elements in dupeGuru
-----------------------------

dupeGuru is designed with a `cross-toolkit`_ approach in mind. It means that its core code
(which doesn't depend on any GUI toolkit) has elements which preformat core information in a way
that makes it easy for a UI layer to consume.

For example, we have :class:`~core.gui.ResultTable` which takes information from
:class:`~core.results.Results` and mashes it in rows and columns which are ready to be fetched by
either Cocoa's ``NSTableView`` or Qt's ``QTableView``. It tells them which cell is supposed to be
blue, which is supposed to be orange, does the sorting logic, holds selection, etc..

.. _cross-toolkit: http://www.hardcoded.net/articles/cross-toolkit-software
"""
