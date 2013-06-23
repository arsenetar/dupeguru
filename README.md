# dupeGuru README

This package contains the source for dupeGuru. To learn how to build it, refer to the
"How to build dupeGuru from source" section. Below is the description of the various subfolders:

* core: Contains the core logic code for dupeGuru. It's Python code.
* core_*: Edition-specific-cross-toolkit code written in Python.
* cocoa: UI code for the Cocoa toolkit. It's Objective-C code.
* qt: UI code for the Qt toolkit. It's written in Python and uses PyQt.
* images: Images used by the different UI codebases.
* debian: Skeleton files required to create a .deb package
* help: Help document, written for Sphinx.

There are also other sub-folder that comes from external repositories and are part of this repo as
git subtrees:

* hscommon: A collection of helpers used across HS applications.
* cocoalib: A collection of helpers used across Cocoa UI codebases of HS applications.
* qtlib: A collection of helpers used across Qt UI codebases of HS applications.

# How to build dupeGuru from source

## Prerequisites installation

Then, you have to make sure that your system has to "non-pip-installable" prerequisites installed:

* All systems: Python 3.2+
* Mac OS X: The last XCode to have the 10.6 SDK included.
* Windows: Visual Studio 2008, PyQt 4.7+, cx_Freeze and Advanced Installer

On Ubuntu, the apt-get command to install all pre-requisites is:

    $ apt-get install python3-dev python3-pyqt4 pyqt4-dev-tools python3-setuptools

## Virtualenv setup

First, you need `pip` and `virtualenv` in your system Python install:

    $ sudo easy_install pip
    $ sudo pip install virtualenv

Then, in dupeGuru's source folder, create a virtual environment and activate it:

    $ virtualenv --system-site-packages env
    $ source env/bin/activate

Then, you can install pip requirements in your virtualenv:

    $ pip install -r requirements-[osx|win].txt
    
([osx|win] depends, of course, on your platform. On other platforms, just use requirements.txt).

## Actual building and running

With your virtualenv activated, you can build and run dupeGuru with these commands:

    $ python configure.py
    $ python build.py
    $ python run.py

You can also package dupeGuru into an installable package with:
    
    $ python package.py
