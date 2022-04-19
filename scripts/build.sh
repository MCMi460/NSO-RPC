cd ../client
python3 -m pip install -r requirements.txt py2app
py2applet --make-setup app.py icon.icns "icon.png" "taskbarDark.png" "taskbarLight.png"
python3 setup.py py2app
open dist
