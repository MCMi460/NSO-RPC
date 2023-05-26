cd ..\client
python -m pip install -r requirements.txt pyinstaller
python -m pip install pypiwin32 winshell
python -m PyInstaller --onefile --clean --noconsole --add-data "*.png;." --icon=icon.ico --name=NSO-RPC app.py
start dist
