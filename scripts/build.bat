cd ..\client
python -m pip install -r requirements.txt pyinstaller
pyinstaller --onefile --clean --noconsole --add-data "*.png;." --icon=icon.ico app.py
start dist
