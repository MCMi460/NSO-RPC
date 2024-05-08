#!/bin/bash
python3 -m venv --upgrade-deps venv
source venv/bin/activate
python3 -m pip install wheel PyQt6
bash prep-PyQt.sh
cd ../../client
python3 -m pip install -r requirements.txt py2app GitPython
python3 _version.py
rm setup.py
py2applet --make-setup app.py icon.icns "icon.png" "taskbarDark.png" "taskbarLight.png" "version.txt"
# build universal binary
sed -i '' -e "s/)/    name='NSO-RPC')/" setup.py
python3 setup.py py2app -O2 --arch=universal2
python3 ../scripts/macos-universal2/debloat-qt.py
# arm64 requires codesigning to run
codesign --deep --force --sign - dist/NSO-RPC.app/Contents/MacOS/*
open dist
