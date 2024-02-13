
@echo on

cd %cd%

python -m pip install --upgrade pip
python -m pip install virtualenv & virtualenv venv & call venv\Scripts\activate
python -m pip install Nuitka
python -m pip install zstandard
python -m pip install chardet

python -m nuitka --onefile --plugin-enable=multiprocessing --windows-disable-console t1.py

pause
