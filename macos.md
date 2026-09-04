## How to build de-dup for macOS
These instructions are for building de-dup and running its native `pywebview` desktop UI on macOS.

### Prerequisites

- [Python 3.10+][python]
- [Xcode 12.3][xcode] or Xcode command line tools
- [Rust & Cargo](https://rustup.rs/) (for compiling the native parallel engine)

#### Prerequisite setup
1. Install Xcode command line tools: `xcode-select --install`
2. Install Python 3.10+ (via Homebrew or python.org)

### Build & Run
de-dup uses standard Python virtual environments and compiles the native Rust extension automatically via `make`:

    $ cd <de-dup directory>
    $ make
    $ make run

### Generate macOS Packages
The extra requirements need to be installed to run packaging: `pip install -r requirements-extra.txt`.
Run the following in the respective virtual environment:

    $ python package.py

This will produce a dupeGuru.app in the dist folder.

### Running tests
The complete test suite can be run with tox just like on linux. NOTE: The extra requirements need to
be installed to run unit tests: `pip install -r requirements-extra.txt`.

[python]: http://www.python.org/
[homebrew]: https://brew.sh/
[xcode]: https://developer.apple.com/xcode/
