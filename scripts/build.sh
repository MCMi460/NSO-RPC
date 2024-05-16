#!/bin/bash
set -e

# Run everything relative to our script directory.
cd "$(dirname "$0")"

# Activate a virtual environment so we don't pollute the system environment.
python3 -m venv --upgrade-deps venv
source venv/bin/activate
cd ../client

# As this is an x86_64 only version, ensure `py2app` outputs x86_64.
python3 -m pip install -r requirements.txt pyqt6 py2app GitPython
python3 _version.py

# Recreate our setup.py with macOS-specific options.
if [ -f setup.py ]; then
  rm setup.py
fi
py2applet --make-setup app.py icon.icns "icon.png" "taskbarDark.png" "taskbarLight.png" "version.txt"
sed -i '' -e "s/)/    name='NSO-RPC')/" setup.py
python3 setup.py py2app --arch=x86_64 -O2
open dist
