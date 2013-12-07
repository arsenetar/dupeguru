Developer Guide
===============

When looking at a non-trivial codebase for the first time, it's very difficult to understand
anything of it until you get the "Big Picture". This page is meant to, hopefully, make you get
dupeGuru's big picture.

Model/View/Controller... nope!
------------------------------

dupeGuru's codebase has quite a few design flaws. The Model, View and Controller roles are filled by
different classes, scattered around. If you're aware of that, it might help you to understand what
the heck is going on.

The central piece of dupeGuru is ``dupeguru.app.DupeGuru`` (in the ``core`` code). It's the only
interface to the python's code for the GUI code. A duplicate scan is started with
``start_scanning()``, directories are added through ``add_directory()``, etc..

A lot of functionalities of the App are implemented in the platform-specific subclasses of
``app.DupeGuru``, like ``app_cocoa.DupeGuru``, or the ``base.app.DupeGuru`` class in the PyQt
codebase. For example, when performing "Remove Selected From Results",
``app_cocoa.Dupeguru.RemoveSelected()`` on the Obj-C side, and
``base.app.DupeGuru.remove_duplicates()`` on the PyQt side, are respectively called to perform the
thing. All of this is quite ugly, I know (see the "Refactoring" section below).

.. _jobs:

Jobs
----

A lot of operations in dupeGuru take a significant amount of time. This is why there's a generalized
threaded job mechanism built-in ``app.DupeGuru``. First, ``app.DupeGuru`` has a ``progress`` member
which is an instance of ``jobprogress.job.ThreadedJobPerformer``. It lets the GUI code know of the
progress of the current threaded job. When ``app.DupeGuru`` needs to start a job, it calls
``_start_job()`` and the platform specific subclass deals with the details of starting the job.

Core principles
---------------

The core of the duplicate matching takes place (for SE and ME, not PE) in ``dupeguru.engine``.
There's ``MatchFactory.getmatches()`` which take a list of ``fs.File`` instances and return a list
of ``(firstfile, secondfile, match_percentage)`` matches. Then, there's ``get_groups()`` which takes
a list of matches and returns a list of ``Group`` instances (a ``Group`` is basically a list of
``fs.File`` matching together).

When a scan is over, the final result (the list of groups from ``get_groups()``) is placed into
``app.DupeGuru.results``, which is a ``results.Results`` instance. The ``Results`` instance is where
all the dupe marking, sorting, removing, power marking, etc. takes place.

API
---

.. toctree::
    :maxdepth: 2
    
    core/index
    hscommon/index
