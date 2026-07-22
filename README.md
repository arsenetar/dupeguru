# dupeGuru (Fork)

> [!NOTE]
> This repository is a customized fork of the original [dupeGuru](https://github.com/arsenetar/dupeguru). It introduces cross-platform configuration file standardization, a robust headless server, and a fully responsive HTML Web Console client for headless/remote execution.

[dupeGuru][dupeguru] is a cross-platform (Linux, OS X, Windows) GUI tool to find duplicate files in
a system. It is written mostly in Python 3 and uses [qt](https://www.qt.io/) for the UI or a modern HTML Web client for server execution.

## Current status
Still looking for additional help especially with regards to:
* OSX maintenance: reproducing bugs, packaging verification.
* Linux maintenance: reproducing bugs, maintaining PPA repository, Debian package, rpm package.
* Translations: updating missing strings, transifex project at https://www.transifex.com/voltaicideas/dupeguru-1
* Documentation: keeping it up-to-date.

## Contents of this folder

This folder contains the source for dupeGuru. Its user documentation is in `help`, and its system-level developer documentation is in `docs`. Here's how this source tree is organized:

* core: Contains the core logic code for dupeGuru. It's Python code.
* qt: UI code for the Qt toolkit. It's written in Python and uses PyQt.
* docs: Contains system-level developer documentation. See the **[Getting Started Guide](file:///Users/tinle/src/tinle/opensource/dupeguru/docs/getting_started.md)** or the **[System Documentation Index](file:///Users/tinle/src/tinle/opensource/dupeguru/docs/index.md)**.
* images: Images used by the different UI codebases.
* pkg: Skeleton files required to create different packages.
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
dupeGuru comes with a Makefile that can be used to build, run, and package the application:

    $ make          # Build all components (C modules, virtualenv, resources)
    $ make run      # Run the standard Qt Desktop application
    $ make web      # Start the local REST server and open the Web UI in your browser
    $ make package  # Build a standalone native executable package for your OS
    $ make release-status   # View release version alignment status

### Running the HTML Web UI Console
dupeGuru includes a responsive, dark-mode Web UI that runs a local REST server. To launch the Web Console:

    $ make web

The server starts by default on `http://localhost:8080` and launches your system browser. To start the server manually on a custom port:

    $ ./env/bin/python run_web.py --port 9090

If you install dupeGuru globally using `sudo make install`, you can start the Web UI from anywhere in your terminal by running:

    $ dupeguru-web

### Key Features

#### 1. HTML Web UI Console
- **Glassmorphic UI**: Clean desktop-like interface optimized for browsers.
- **Direct Directory Browser**: Walk local paths and target directories for duplicate detection.
- **Config Management**: Toggle preferences (Filter Hardness, Regexp matching, Ignored Hardlinks, Checkpoints) directly in the sidebar panel.
- **Save & Load Scans**: Save current results or load previous `.dupegururesults` files.

#### 2. SQLite Database Checkpoints & Resumption
- **Regular Checkpoints**: dupeGuru flushes metadata to the SQLite cache database at a user-configurable frequency (default: 100 files). This prevents filesystem corruption, particularly on network-mounted drives.
- **Stop & Resume**: Stopping a scan commits all progress to the cache. Running the scan again on the same folders instantly skips already scanned files and resumes where you left off.

#### 3. High-Scale Low-Memory Pipeline
- **Generator-Streamed Discovery**: Avoids loading millions of file paths into memory at once, using memory-efficient SQLite indexing and custom generators to handle scans of any size in $O(1)$ memory.
- **Size-Batching Hashing**: Groups and processes candidates in size batches of 2,000 to keep the memory footprint under 150 MB even when scanning millions of files.
- **Transitive Exact Match Optimizations**: Drastically reduces grouping set operations and prunes redundant duplicate-to-duplicate matches, shrinking memory overhead from $O(N^2)$ to $O(N)$.
- **Paginated UI API**: Server-side pagination limits network data transfer and browser rendering stress by loading results in small pages of 50 groups.

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
