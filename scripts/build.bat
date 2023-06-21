@echo off

cd ..\client

REM Create a temporary Python script to discover usable PyQt modules. 
set "temp_dir=%TEMP%\NSO-RPC\temp"
mkdir "%temp_dir%"
set "temp_script=%temp_dir%\temp.py"
echo import sys > "%temp_script%"
echo PYQT_PACKAGE = '' >> "%temp_script%"
echo try: >> "%temp_script%"
echo     from PyQt6.QtWidgets import QApplication >> "%temp_script%"
echo     PYQT_PACKAGE = 'PyQt6' >> "%temp_script%"
echo except ImportError: >> "%temp_script%"
echo     try: >> "%temp_script%"
echo         from PyQt5.QtWidgets import QApplication >> "%temp_script%"
echo         PYQT_PACKAGE = 'PyQt5' >> "%temp_script%"
echo     except ImportError: >> "%temp_script%"
echo         print('PyQt6 or PyQt5 is required. Please install either of them.', file=sys.stderr) >> "%temp_script%"
echo         sys.exit(1) >> "%temp_script%"
echo print(PYQT_PACKAGE) >> "%temp_script%"
for /f "usebackq tokens=*" %%G in (`python "%temp_script%"`) do (
    set "PYQT_PACKAGE=%%G"
)
rmdir /s /q "%temp_dir%"
REM Check if PyQt package is set
if "%PYQT_PACKAGE%"=="" (
    exit /b 1
)
echo Building with %PYQT_PACKAGE%

REM Install requirements
python -m pip install -r ./requirements.txt pypiwin32 winshell pyinstaller==5.10.1 pyinstaller-hooks-contrib==2023.2

REM Build the executable using PyInstaller
python -m PyInstaller --onefile --clean --noconsole --exclude-module autopep8 --noupx --add-data "*.png;." --icon=icon.ico --name=NSO-RPC ..\client\app.py

REM Open the 'dist' directory
start .\dist