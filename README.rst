Contents
========

This package contains the source for dupeGuru. To learn how to build it, refer to the
"Build dupeGuru" section. Below is the description of the various subfolders:

- core: Contains the core logic code for dupeGuru. It's Python code.
- core_*: Edition-specific-cross-toolkit code written in Python.
- cocoa: UI code for the Cocoa toolkit. It's Objective-C code.
- qt: UI code for the Qt toolkit. It's written in Python and uses PyQt.
- images: Images used by the different UI codebases.
- debian: Skeleton files required to create a .deb package
- help: Help document, written for Sphinx.

There are also other sub-folder that comes from external repositories (automatically checked out
as mercurial subrepos):

- hscommon: A collection of helpers used across HS applications.
- cocoalib: A collection of helpers used across Cocoa UI codebases of HS applications.
- qtlib: A collection of helpers used across Qt UI codebases of HS applications.

dupeGuru Dependencies
=====================

Before being able to build dupeGuru, a few dependencies have to be installed. If you use pip, you
will not have to install them all manually (see "The easy way!" below):

General dependencies
--------------------

- Python 3.2 (http://www.python.org)
- Send2Trash3k (http://hg.hardcoded.net/send2trash)
- hsaudiotag3k 1.1.0 (for ME) (http://hg.hardcoded.net/hsaudiotag)
- jobprogress 1.0.3 (http://hg.hardcoded.net/jobprogress)
- Sphinx 1.1 (http://sphinx.pocoo.org/)
- polib 0.7.0 (http://bitbucket.org/izi/polib)
- pytest 2.0.0, to run unit tests. (http://pytest.org/)

OS X prerequisites
------------------

- XCode's command line tools
- objp 1.1.0 (http://bitbucket.org/hsoft/objp)
- appscript 1.0.0 for ME and PE (http://appscript.sourceforge.net/)
- xibless 0.4.0 (https://bitbucket.org/hsoft/xibless)

Windows prerequisites
---------------------

- Visual Studio 2008 (Express is enough) is needed to build C extensions. (http://www.microsoft.com/Express/)
- PyQt 4.7+ (http://www.riverbankcomputing.co.uk/news)
- cx_Freeze, if you want to build a exe. You don't need it if you just want to run dupeGuru. (http://cx-freeze.sourceforge.net/)
- Advanced Installer, if you want to build the installer file. (http://www.advancedinstaller.com/)

Linux prerequisites
-------------------

- PyQt 4.7+ (http://www.riverbankcomputing.co.uk/news)

The easy way!
-------------

There's an easy way to install the majority of the prerequisites above, and it's `pip <http://www.pip-installer.org/>`_ which has recently started to support Python 3. So install it and then run::

    pip install -r requirements-[osx|win].txt

([osx|win] depends, of course, on your platform. On other platforms, just use requirements.txt). 

Advanced Installer, having nothing to do with Python, needs to be installed manually.

PyQt isn't in the requirements file either (there's no package uploaded on PyPI) and you also have
to install it manually.

If you use a virtualenv (which you should), you have to enable the "site-packages" option because
dupeGuru will need the PyQt library which you'll have installed on your system.

Prerequisite gotchas
--------------------

Correctly installing the prerequisites is tricky. Make sure you have at least the version number 
required for each prerequisite.

If you didn't use mercurial to download this source, you probably have an incomplete source folder!
External projects (hscommon, qtlib, cocoalib) need to be at the root of the dupeGuru project folder.
You'll have to download those separately. Or use mercurial, it's much easier.

Another one on OS X: I wouldn't use macports/fink/whatever. Whenever I tried using those, I always 
ended up with problems.

Whenever you have a problem, always double-check that you're running the correct python version. 
You'll probably have to tweak your $PATH.

To setup a build machine under Ubuntu 12.04 and up, install those packages: python3-dev, python3-pyqt4,
pyqt4-dev-tools, mercurial and then python3-setuptools. Once you've done that, install pip with
`easy_install`. Once you've done that, you can then perform "The easy way!" installation.

Building dupeGuru
=================

First, make sure you meet the dependencies listed in the section above. Then you need to configure
your build with::

	python configure.py

If you want, you can specify a UI to use with the ``--ui`` option. So, if you want to build dupeGuru
with Qt on OS X, then you have to type ``python configure.py --ui=qt``. You can also use the
``--dev`` flag to indicate a dev build (mostly useful in OS X, where the python code in symlinked
so you don't have to repackage whenever you make a change in the python code).

Then, just build the thing and then run it with::

	python build.py
	python run.py

If you want to create ready-to-upload package, run::

	python package.py
