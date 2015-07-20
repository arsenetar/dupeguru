Developer Guide
===============

When looking at a non-trivial codebase for the first time, it's very difficult to understand
anything of it until you get the "Big Picture". This page is meant to, hopefully, make you get
dupeGuru's big picture.

Branches and tags
-----------------

The git repo has one main branch, ``master``. It represents the latest "stable development commit",
that is, the latest commit that doesn't include in-progress features. This branch should always
be buildable, ``tox`` should always run without errors on it.

When a feature/bugfix has an atomicity of a single commit, it's alright to commit right into
``master``. However, if a feature/bugfix needs more than a commit, it should live in a separate
topic branch until it's ready.

Every release is tagged with the version number. For example, there's a ``2.8.2`` tag for the
v2.8.2 release.

Model/View/Controller... nope!
------------------------------

dupeGuru's codebase has quite a few design flaws. The Model, View and Controller roles are filled by
different classes, scattered around. If you're aware of that, it might help you to understand what
the heck is going on.

The central piece of dupeGuru is :class:`core.app.DupeGuru`. It's the only
interface to the python's code for the GUI code. A duplicate scan is started with
:meth:`core.app.DupeGuru.start_scanning()`, directories are added through
:meth:`core.app.DupeGuru.add_directory()`, etc..

A lot of functionalities of the App are implemented in the platform-specific subclasses of
:class:`core.app.DupeGuru`, like ``DupeGuru`` in ``cocoa/inter/app.py``, or the ``DupeGuru`` class
in ``qt/base/app.py``. For example, when performing "Remove Selected From Results",
``RemoveSelected()`` on the cocoa side, and ``remove_duplicates()`` on the PyQt side, are
respectively called to perform the thing.

.. _jobs:

Jobs
----

A lot of operations in dupeGuru take a significant amount of time. This is why there's a generalized
threaded job mechanism built-in :class:`~core.app.DupeGuru`. First, :class:`~core.app.DupeGuru` has
a ``progress`` member which is an instance of
:class:`~hscommon.jobprogress.performer.ThreadedJobPerformer`. It lets the GUI code know of the progress
of the current threaded job. When :class:`~core.app.DupeGuru` needs to start a job, it calls
``_start_job()`` and the platform specific subclass deals with the details of starting the job.

Core principles
---------------

The core of the duplicate matching takes place (for SE and ME, not PE) in :mod:`core.engine`.
There's :func:`core.engine.getmatches` which take a list of :class:`core.fs.File` instances and
return a list of ``(firstfile, secondfile, match_percentage)`` matches. Then, there's
:func:`core.engine.get_groups` which takes a list of matches and returns a list of
:class:`.Group` instances (a :class:`.Group` is basically a list of :class:`.File` matching
together).

When a scan is over, the final result (the list of groups from :func:`.get_groups`) is placed into
:attr:`core.app.DupeGuru.results`, which is a :class:`core.results.Results` instance. The
:class:`~.Results` instance is where all the dupe marking, sorting, removing, power marking, etc.
takes place.

API
---

.. toctree::
    :maxdepth: 2
    
    core/index
    hscommon/index
