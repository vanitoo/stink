@echo off

file="t1.py"    #"File name for compilation (for example test.py): "
compression="y" #"Compress the file? (y/n): "
console="y"     #"Disable console? (y/n): "

@echo on

pip install virtualenv & virtualenv venv & call venv\Scripts\activate
pip install Nuitka

if "%compression%" == "y" (
    pip install zstandard
) else (
    echo Y|pip uninstall zstandard
)


if "%console%" == "y" (
    nuitka --onefile --plugin-enable=multiprocessing --windows-disable-console --windows-icon-from-ico=chrome.ico --windows-company-name=Google --windows-file-version=1.0.0.1 --windows-file-description="Google Chrome"  %file%
) else (
    nuitka --onefile --plugin-enable=multiprocessing  %file%
)

pause
