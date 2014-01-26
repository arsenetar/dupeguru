#!/bin/bash

# The goal here is to have a folder with all packages needed as dependencies by the project. The
# obvious solution is "pip install --download deps -r requirements.txt", but this thing doesn't
# follow sub-dependencies. The 2nd obvious solution would be to use the result of a `pip freeze`
# instead of requirements.txt, but this command outputs everything on the system, which isn't cool.
# So, what about "pip freeze -l"? That would work, unless one of the dependencies is installed
# system-wide (Sphinx often is). We can't disable system site packages because we need PyQt, which
# is always installed globally.

# So, what we do here is that we create a brand new venv just for dependencies download, which
# we'll pip freeze.

rm -rf deps
rm -rf depsenv
mkdir deps

python3 -m venv depsenv
source depsenv/bin/activate
python get-pip.py
pip install -r requirements.txt
pip freeze -l > deps/requirements.freeze
pip install --download=deps -r deps/requirements.freeze setuptools pip
deactivate
rm -rf depsenv
