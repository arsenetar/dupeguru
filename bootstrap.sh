#!/bin/bash

command -v python3 -m venv >/dev/null 2>&1 || { echo >&2 "Python 3.3 required. Install it and try again. Aborting"; exit 1; }

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
    python3 -m venv env
    source env/bin/activate
    if python -m ensurepip; then
        echo "We're under Python 3.4+, no need to try to install pip!"
    else
        python get-pip.py $PIPARGS --force-reinstall
    fi
    deactivate
    python3 -m venv env --upgrade --system-site-packages
fi

source env/bin/activate

echo "Installing pip requirements"
if [ "$(uname)" == "Darwin" ]; then
    pip install $PIPARGS -r requirements-osx.txt
else
    python3 -c "import PyQt5" >/dev/null 2>&1 || { echo >&2 "PyQt 5.1+ required. Install it and try again. Aborting"; exit 1; }
    pip install $PIPARGS -r requirements.txt
fi

echo "Bootstrapping complete! You can now configure, build and run dupeGuru with:"
echo ". env/bin/activate && python configure.py && python build.py && python run.py"
