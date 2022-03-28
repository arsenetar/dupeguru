## How to build dupeGuru for macos
These instructions are for the Qt version of the UI on macOS.

*Note: The Cocoa UI of dupeGuru is hosted in a separate repo: https://github.com/arsenetar/dupeguru-cocoa and is no longer "supported".*
### Prerequisites

- [Python 3.7+][python]
- [Xcode 12.3][xcode] or just Xcode command line tools (older versions can be used if not interested in arm macs)
- [Homebrew][homebrew]
- [qt5](https://www.qt.io/)

#### Prerequisite setup
1. Install Xcode if desired
2. Install [Homebrew][homebrew], if not on the path after install (arm based Macs) create `~/.zshrc` 
with `export PATH="/opt/homebrew/bin:$PATH"`. Will need to reload terminal or source the file to take 
effect.
3. Install qt5 with `brew`. If you are using a version of macos without system python 3.7+ then you will 
also need to install that via brew or with pyenv.

        $ brew install qt5

    NOTE: Using `brew` to install qt5 is to allow pyqt5 to build without a native wheel
    available.  If you are using an intel based mac you can probably skip this step.

4. May need to launch a new terminal to have everything working.

### With build.py
OSX comes with a version of python 3 by default in newer versions of OSX.  To produce universal 
builds either the 3.8 version shipped in macos or 3.9.1 or newer needs to be used. If needing to
build pyqt5 from source then the first line below is needed, else it may be omitted. (Path shown is 
for an arm mac.)

    $ export PATH="/opt/homebrew/opt/qt/bin:$PATH"
    $ cd <dupeGuru directory>
    $ python3 -m venv ./env
    $ source ./env/bin/activate
    $ pip install -r requirements.txt
    $ python build.py
    $ python run.py

### Generate OSX Packages
The extra requirements need to be installed to run packaging: `pip install -r requirements-extra.txt`. 
Run the following in the respective virtual environment.

    $ python package.py

This will produce a dupeGuru.app in the dist folder.

### Running tests
The complete test suite can be run with tox just like on linux. NOTE: The extra requirements need to 
be installed to run unit tests: `pip install -r requirements-extra.txt`.

[python]: http://www.python.org/
[homebrew]: https://brew.sh/
[xcode]: https://developer.apple.com/xcode/
