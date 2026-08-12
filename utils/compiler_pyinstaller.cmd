@echo off

set /p file="File name for compilation (for example test.py): "
set /p console="Disable console? (y/n): "

@echo on

pip install virtualenv & virtualenv venv & call .venv\Scripts\activate
pip install pyinstaller

if "%console%" == "y" (
    pyinstaller --onefile --clean --strip %file%
) else (
    pyinstaller --onefile --clean --strip --windowed %file%
)

pause