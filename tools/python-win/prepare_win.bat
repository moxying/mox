@echo off


echo download python-3.10.11-embed-amd64.zip
@REM curl https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip -o python-embeded.zip
@REM powershell Expand-Archive python-embeded.zip -DestinationPath python-embeded
@REM del /f /q python-embeded.zip
cd python-embeded
@REM echo import site>> ./python310._pth

echo download get-pip.py
@REM curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

echo run get-pip.py
@REM .\python.exe -s get-pip.py

echo pip install deps
@REM .\python.exe -s -m pip install torch torchvision torchaudio
@REM .\python.exe -s -m pip install -r ..\..\..\agent\requirements.txt