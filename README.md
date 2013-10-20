# dupeGuru

This package contains the source for dupeGuru. Its documentation is
[available online][documentation]. Here's how this source tree is organised:

* core: Contains the core logic code for dupeGuru. It's Python code.
* core_*: Edition-specific-cross-toolkit code written in Python.
* cocoa: UI code for the Cocoa toolkit. It's Objective-C code.
* qt: UI code for the Qt toolkit. It's written in Python and uses PyQt.
* images: Images used by the different UI codebases.
* debian: Skeleton files required to create a .deb package
* help: Help document, written for Sphinx.
* locale: .po files for localisation.

There are also other sub-folder that comes from external repositories and are part of this repo as
git subtrees:

* hscommon: A collection of helpers used across HS applications.
* cocoalib: A collection of helpers used across Cocoa UI codebases of HS applications.
* qtlib: A collection of helpers used across Qt UI codebases of HS applications.

# How to build dupeGuru from source

## The very, very, very easy way

If you're on Linux or Mac, there's a bootstrap script that will make building very, very easy. There
might be some things that you need to install manually on your system, but the bootstrap script will
tell you when what you need to install. You can run the bootstrap with:

    ./bootstrap.sh

and follow instructions from the script. You can then ignore the rest of the build documentation.

## Prerequisites installation

Prerequisites are installed through `pip`. However, some of them are not "pip installable" and have
to be installed manually.

* All systems: [Python 3.3+][python] and [setuptools][setuptools]
* Mac OS X: The last XCode to have the 10.6 SDK included.
* Windows: Visual Studio 2010, [PyQt 5.0+][pyqt], [cx_Freeze][cxfreeze] and
  [Advanced Installer][advinst] (you only need the last two if you want to create an installer)

On Ubuntu (13.10+), the apt-get command to install all pre-requisites is:

    $ apt-get install python3-dev python3-pyqt5 pyqt5-dev-tools

On Arch, it's:

    $ pacman -S python-pyqt5

## Virtualenv setup

Use the built-in `pyvenv` to setup a virtual environment, and then install `pip` and run the
requirements in it:

    $ pyvenv --system-site-packages env
    $ source env/bin/activate
    $ wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - | python
    $ easy_install pip

## Actual building and running

With your virtualenv activated, you can build and run dupeGuru with these commands:

    $ python configure.py
    $ python build.py
    $ python run.py

You can also package dupeGuru into an installable package with:
    
    $ python package.py

[documentation]: http://www.hardcoded.net/dupeguru/help/en/
[python]: http://www.python.org/
[setuptools]: https://pypi.python.org/pypi/setuptools
[pyqt]: http://www.riverbankcomputing.com
[cxfreeze]: http://cx-freeze.sourceforge.net/
[advinst]: http://www.advancedinstaller.com
