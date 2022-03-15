## How to build dupeGuru for Windows

### Prerequisites

- [Python 3.7+][python]
- [Visual Studio 2019][vs] or [Visual Studio Build Tools 2019][vsBuildTools] with the Windows 10 SDK
- [nsis][nsis] (for installer creation)
- [msys2][msys2] (for using makefile method)

NOTE: When installing Visual Studio or the Visual Studio Build Tools with the Windows 10 SDK on versions of Windows below 10 be sure to make sure that the Universal CRT is installed before installing Visual studio as noted in the [Windows 10 SDK Notes][win10sdk] and found at [KB2999226][KB2999226].

After installing python it is recommended to update setuptools before compiling packages.  To update run (example is for python launcher and 3.8):

    $ py -3.8 -m pip install --upgrade setuptools

More details on setting up python for compiling packages on windows can be found on the [python wiki][pythonWindowsCompilers] Take note of the required vc++ versions.

### With build.py (preferred)
To build with a different python version 3.7 vs 3.8 or 32 bit vs 64 bit specify that version instead of -3.8 to the `py` command below.  If you want to build additional versions while keeping all virtual environments setup use a different location for each virtual environment.

    $ cd <dupeGuru directory>
    $ py -3.8 -m venv .\env
    $ .\env\Scripts\activate
    $ pip install -r requirements.txt
    $ python build.py
    $ python run.py

### With makefile
It is possible to build dupeGuru with the makefile on windows using a compatable POSIX environment.  The following steps have been tested using [msys2][msys2]. Before running make:
1. Install msys2 or other POSIX environment
2. Install PyQt5 globally via pip
3. Use the respective console for msys2 it is `msys2 msys` 

Then the following execution of the makefile should work.  Pass the correct value for PYTHON to the makefile if not on the path as python3.

    $ cd <dupeGuru directory>
    $ make PYTHON='py -3.8'
    $ make run

### Generate Windows Installer Packages
You need to use the respective x86 or x64 version of python to build the 32 bit and 64 bit versions.  The build scripts will automatically detect the python architecture for you. When using build.py make sure the resulting python works before continuing to package.py.  NOTE: package.py looks for the 'makensis' executable in the default location for a 64 bit windows system.  The extra requirements need to be installed to run packaging: `pip install -r requirements-extra.txt`. Run the following in the respective virtual environment.

    $ python package.py

### Running tests
The complete test suite can be run with tox just like on linux. NOTE: The extra requirements need to be installed to run unit tests: `pip install -r requirements-extra.txt`.

[python]: http://www.python.org/
[nsis]: http://nsis.sourceforge.net/Main_Page
[vs]: https://www.visualstudio.com/downloads/#visual-studio-community-2019
[vsBuildTools]: https://www.visualstudio.com/downloads/#build-tools-for-visual-studio-2019
[win10sdk]: https://developer.microsoft.com/en-us/windows/downloads/windows-10-sdk
[KB2999226]: https://support.microsoft.com/en-us/help/2999226/update-for-universal-c-runtime-in-windows
[pythonWindowsCompilers]: https://wiki.python.org/moin/WindowsCompilers
[msys2]: http://www.msys2.org/
