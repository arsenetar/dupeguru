## How to build dupeGuru for Windows

### Prerequisites

- [Python 3.4+][python]
- [nsis](http://nsis.sourceforge.net/Main_Page) (for installer creation)

### With build.py (preferred)
To build with a different python version 3.5 vs 3.6 or 32 bit vs 64 bit specify that version instead of -3.5 to the `py` command below.  If you want to build additional versions while keeping all virtual environments setup use a different location for each vritual environment.

    $ cd <dupeGuru directory>
    $ git submodule init
    $ git submodule update
    $ py -3.5 -m venv .\env
    $ .\env\Scripts\activate
    $ pip install -r requirements.txt -r requirements-windows.txt
    $ python build.py
    $ python run.py

### With makefile
It is possible to build dupeGuru with the makefile on windows using msys2. There are a few additional considerations:
1. Install PyQt5 globally
2. pass the correct value for PYTHON to the makefile if not on the path as python3
3. Install PyQt5 & cx-Freeze with requirements-windows.txt into the venv 

Then the following should work

    $ make PYTHON='py -3.5'
    $ make run

### Generate Windows Installer Packages
You need to use the respective x86 or x64 version of python to build the 32 bit and 64 bit versions. The build scripts will automatically detect the python architecture for you. When using build.py make sure the resulting python works before continuing to package.py. NOTE: package.py looks for the 'makensis' executable in the default location for a 64 bit windows system.

    $ python package.py

### Running tests
The complete test suite can be run with tox just like on linux.
