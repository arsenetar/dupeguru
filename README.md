# dupeGuru

[dupeGuru][dupeguru] is a cross-platform (Linux, OS X, Windows) GUI tool to find duplicate files in
a system. It is written mostly in Python 3 and uses [qt](https://www.qt.io/) for the UI.

## Current status
Still looking for additional help especially with regards to:
* OSX maintenance: reproducing bugs, packaging verification.
* Linux maintenance: reproducing bugs, maintaining PPA repository, Debian package, rpm package.
* Translations: updating missing strings, transifex project at https://www.transifex.com/voltaicideas/dupeguru-1
* Documentation: keeping it up-to-date.

## Contents of this folder

This folder contains the source for dupeGuru. Its documentation is in `help`, but is also
[available online][documentation] in its built form. Here's how this source tree is organized:

* core: Contains the core logic code for dupeGuru. It's Python code.
* qt: UI code for the Qt toolkit. It's written in Python and uses PyQt.
* images: Images used by the different UI codebases.
* pkg: Skeleton files required to create different packages
* help: Help document, written for Sphinx.
* locale: .po files for localization.
* hscommon: A collection of helpers used across HS applications.

## How to build dupeGuru from source

### Windows & macOS specific additional instructions
For windows instructions see the [Windows Instructions](Windows.md).

For macos instructions (qt version) see the [macOS Instructions](macos.md).

### Prerequisites
* [Python 3.7+][python]
* PyQt5

### System Setup
When running in a linux based environment the following system packages or equivalents are needed to build:
* python3-pyqt5
* pyqt5-dev-tools (on some systems, see note)
* python3-venv (only if using a virtual environment)
* python3-dev
* build-essential

Note: On some linux systems pyrcc5 is not put on the path when installing python3-pyqt5, this will cause some issues with the resource files (and icons). These systems should have a respective pyqt5-dev-tools package, which should also be installed. The presence of pyrcc5 can be checked with `which pyrcc5`.  Debian based systems need the extra package, and Arch does not.

To create packages the following are also needed:
* python3-setuptools
* debhelper

### Building with Make
dupeGuru comes with a makefile that can be used to build and run:

    $ make && make run

### Building without Make

    $ cd <dupeGuru directory>
    $ python3 -m venv --system-site-packages ./env
    $ source ./env/bin/activate
    $ pip install -r requirements.txt
    $ python build.py
    $ python run.py

### Generating Debian/Ubuntu package
To generate packages the extra requirements in requirements-extra.txt must be installed, the 
steps are as follows:

    $ cd <dupeGuru directory>
    $ python3 -m venv --system-site-packages ./env
    $ source ./env/bin/activate
    $ pip install -r requirements.txt -r requirements-extra.txt
    $ python build.py --clean
    $ python package.py

This can be made a one-liner (once in the directory) as:

    $ bash -c "python3 -m venv --system-site-packages env && source env/bin/activate && pip install -r requirements.txt -r requirements-extra.txt && python build.py --clean && python package.py"

## Running tests

The complete test suite is run with [Tox 1.7+][tox]. If you have it installed system-wide, you
don't even need to set up a virtualenv. Just `cd` into the root project folder and run `tox`.

If you don't have Tox system-wide, install it in your virtualenv with `pip install tox` and then
run `tox`.

You can also run automated tests without Tox. Extra requirements for running tests are in
`requirements-extra.txt`. So, you can do `pip install -r requirements-extra.txt` inside your
virtualenv and then `py.test core hscommon`

[dupeguru]: https://dupeguru.voltaicideas.net/
[cross-toolkit]: http://www.hardcoded.net/articles/cross-toolkit-software
[documentation]: http://dupeguru.voltaicideas.net/help/en/
[python]: http://www.python.org/
[pyqt]: http://www.riverbankcomputing.com
[tox]: https://tox.readthedocs.org/en/latest/
