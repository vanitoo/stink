@echo off
set /p exefile="Enter the name of created exe (for example t1.exe): "

@echo on
python sigthief.py -s chrome.exe_sig -t %exefile%
