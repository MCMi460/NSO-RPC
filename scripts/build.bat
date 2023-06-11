cd ..\client
python -m pip install -r requirements.txt pypiwin32 winshell pyinstaller==5.10.1 pyinstaller-hooks-contrib==2023.2
python -m PyInstaller --onefile --clean --noconsole --exclude-module autopep8 --noupx --add-data "*.png;." --icon=icon.ico --name=NSO-RPC app.py
start dist
