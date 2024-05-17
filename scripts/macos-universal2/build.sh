#!/bin/bash
set -e

# Run everything relative to our script directory.
cd "$(dirname "$0")"

# Within GitHub Actions and similar, we should use the Python.org
# copy of Python 3.11 available. This permits a universal2 framework for py2app.
# (Otherwise, GitHub's default runners include a single architecture version.)
if [[ "$CI" == "true" ]]; then
  shopt -s expand_aliases
  alias python3=/Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11
fi

# Activate a virtual environment so we don't pollute the system environment.
python3 -m venv --upgrade-deps venv
source venv/bin/activate
python3 -m pip install wheel

# Before we install anything further, create our custom universal2 version of
# the PyQt6 frameworks (PyQt6_Qt6), and then install PyQt6 itself.
bash prep-PyQt.sh
python3 -m pip install PyQt6

# Lastly, build our client.
cd ../../client
python3 -m pip install -r requirements.txt py2app GitPython
python3 _version.py

# Recreate our setup.py with macOS-specific options.
if [ -f setup.py ]; then
  rm setup.py
fi
py2applet --make-setup app.py icon.icns "icon.png" "taskbarDark.png" "taskbarLight.png" "version.txt"
# build universal binary
sed -i '' -e "s/)/    name='NSO-RPC')/" setup.py
python3 setup.py py2app -O2 --arch=universal2
# arm64 requires codesigning to run
codesign --deep --force --sign - dist/NSO-RPC.app/Contents/MacOS/*
open dist
