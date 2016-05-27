#!/bin/bash

PYTHON=python3
ret=`$PYTHON -c "import sys; print(int(sys.version_info[:2] >= (3, 4)))"`
if [ $ret -ne 1 ]; then
    echo "Python 3.4+ required. Aborting."
    exit 1
fi


if [ -d ".git" ]; then
    git submodule init
    git submodule update
fi

if [ -d "deps" ]; then
    # We have a collection of dependencies in our source package. We might as well use it instead
    # of downloading it from PyPI.
    PIPARGS="--no-index --find-links=deps"
fi

if [ ! -d "env" ]; then
    echo "No virtualenv. Creating one"
    # We need a "system-site-packages" env to have PyQt, but we also need to ensure a local pip
    # install. To achieve our latter goal, we start with a normal venv, which we later upgrade to
    # a system-site-packages once pip is installed.
    if ! $PYTHON -m venv env ; then
        echo "Creation of our virtualenv failed. If you're on Ubuntu, you probably need python3-venv."
        exit 1
    fi
    if [ "$(uname)" != "Darwin" ]; then
        $PYTHON -m venv env --upgrade --system-site-packages
    fi
fi

source env/bin/activate

echo "Installing pip requirements"
if [ "$(uname)" == "Darwin" ]; then
    ./env/bin/pip install $PIPARGS -r requirements-osx.txt
else
    ./env/bin/python -c "import PyQt5" >/dev/null 2>&1 || { echo >&2 "PyQt 5.4+ required. Install it and try again. Aborting"; exit 1; }
    ./env/bin/pip install $PIPARGS -r requirements.txt
fi

echo "Bootstrapping complete! You can now configure, build and run dupeGuru with:"
echo ". env/bin/activate && python configure.py && python build.py && python run.py"
