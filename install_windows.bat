@echo off
setlocal

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Downloading and installing Python...
    REM Download the latest Python installer
    powershell -Command "Start-BitsTransfer -Source https://www.python.org/ftp/python/3.10.12/python-3.10.12-amd64.exe -Destination %temp%\python_installer.exe"
    REM Run the installer with default options
    %temp%\python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    if %errorlevel% neq 0 (
        echo Failed to install Python.
        exit /b %errorlevel%
    )
    echo Python installed successfully.
) else (
    echo Python is already installed.
)

REM Upgrade pip to the latest version
python -m pip install --upgrade pip

REM Install requirements
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install required packages.
    exit /b %errorlevel%
)

REM Run the script
python main.py
if %errorlevel% neq 0 (
    echo Failed to execute main.py
    exit /b %errorlevel%
)

endlocal
exit /b %errorlevel%
