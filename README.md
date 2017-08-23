# dupeGuru

[dupeGuru][dupeguru] is a cross-platform (Linux, OS X, Windows) GUI tool to find duplicate files in
a system. It's written mostly in Python 3 and has the peculiarity of using
[multiple GUI toolkits][cross-toolkit], all using the same core Python code. On OS X, the UI layer
is written in Objective-C and uses Cocoa. On Linux, it's written in Python and uses Qt5.

The Cocoa UI of dupeGuru is hosted in a separate repo: https://github.com/hsoft/dupeguru-cocoa

## Current status: People wanted

dupeGuru has currently only one maintainer, me. This is a dangerous situation that needs to be
corrected.

The goal is to eventually have another active maintainer, but before we can get there, the project
needs more contributors. It is very much lacking on that side right now.

Whatever your skills, if you are remotely interestested in being a contributor, I'm interested in
mentoring you. If that's the case, please refer to [the open ticket on the subject][contrib-issue]
and let's get started.

### Slowed development

Until I manage to find contributors, I'm slowing the development pace of dupeGuru. I'm not much
interested in maintaining it alone, I personally have no use for this app (it's been a *loooong*,
time since I had dupe problems :) )

I don't want to let it die, however, so I will still do normal maintainership, that is, issue
triaging, code review, critical bugfixes, releases management.

But anything non-critical, I'm not going to implement it myself because I see every issue as a
contribution opportunity.

### Windows maintainer wanted

As [described on my website][nowindows], dupeGuru v4.0 dropped Windows support
because there isn't anyone to bear the burden of Windows maintenance.  If
you're a Windows developer and are interested in taking this task, [don't
hesitate to let me know][contrib-issue].

### OS X maintainer wanted

My Mac Mini is already a couple of years old and is likely to be my last Apple purchase. When it
dies, I will be unable maintain the OS X version of moneyGuru. I've already stopped paying for the
Mac Developer membership so I can't sign the apps anymore (in the "official way" I mean. The
download is still PGP signed) If you're a Mac developer and are interested in taking this task,
[don't hesitate to let me know][contrib-issue].

## Contents of this folder

This folder contains the source for dupeGuru. Its documentation is in `help`, but is also
[available online][documentation] in its built form. Here's how this source tree is organised:

* core: Contains the core logic code for dupeGuru. It's Python code.
* qt: UI code for the Qt toolkit. It's written in Python and uses PyQt.
* images: Images used by the different UI codebases.
* pkg: Skeleton files required to create different packages
* help: Help document, written for Sphinx.
* locale: .po files for localisation.

There are also other sub-folder that comes from external repositories and are part of this repo as
git submodules:

* hscommon: A collection of helpers used across HS applications.
* qtlib: A collection of helpers used across Qt UI codebases of HS applications.

## How to build dupeGuru from source

### Windows
For windows instructions see the [Windows Instructions](Windows.md).

### Prerequisites

* [Python 3.4+][python]
* PyQt5

### make

dupeGuru is built with "make":

    $ make
    $ make run

### Generate Ubuntu packages

    $ bash -c "pyvenv --system-site-packages env && source env/bin/activate && pip install -r requirements.txt && python3 build.py --clean && python3 package.py"

### Running tests

The complete test suite is run with [Tox 1.7+][tox]. If you have it installed system-wide, you
don't even need to set up a virtualenv. Just `cd` into the root project folder and run `tox`.

If you don't have Tox system-wide, install it in your virtualenv with `pip install tox` and then
run `tox`.

You can also run automated tests without Tox. Extra requirements for running tests are in
`requirements-extra.txt`. So, you can do `pip install -r requirements-extra.txt` inside your
virtualenv and then `py.test core hscommon`

[dupeguru]: https://www.hardcoded.net/dupeguru/
[cross-toolkit]: http://www.hardcoded.net/articles/cross-toolkit-software
[contrib-issue]: https://github.com/hsoft/dupeguru/issues/300
[nowindows]: https://www.hardcoded.net/archive2015#2015-11-01
[documentation]: http://www.hardcoded.net/dupeguru/help/en/
[python]: http://www.python.org/
[pyqt]: http://www.riverbankcomputing.com
[tox]: https://tox.readthedocs.org/en/latest/