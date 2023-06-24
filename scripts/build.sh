cd ../client
python3 -m pip install -r requirements.txt py2app
py2applet --make-setup app.py icon.icns "icon.png" "taskbarDark.png" "taskbarLight.png"
sed -i '' -e "s/)/    name='NSO-RPC')/" setup.py
# build universal binary
python3 setup.py py2app -O2 --arch=universal2
# arm64 requires codesigning to run
codesign --deep --force --sign - dist/NSO-RPC.app/Contents/MacOS/*
open dist
