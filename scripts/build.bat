cd ..\client
python -m pip install -r requirements.txt pyinstaller
python -m PyInstaller --onefile --clean --noconsole --add-data "*.png;." --icon=icon.ico --name=NSO-RPC app.py
start dist
