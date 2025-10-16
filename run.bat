@echo off
REM ===================================================================
REM  AI ATTENDANCE SYSTEM - LAUNCHER
REM  Hệ thống chấm công thông minh với Anti-Spoofing
REM ===================================================================

echo.
echo ============================================================
echo    AI ATTENDANCE SYSTEM - ANTI-SPOOFING
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python chua duoc cai dat!
    echo Vui long tai Python tu: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python da duoc cai dat
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [WARNING] Virtual environment chua duoc tao!
    echo [INFO] Dang tao virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Khong the tao virtual environment!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment da duoc tao
    echo.
)

REM Activate virtual environment
echo [INFO] Kich hoat virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Khong the kich hoat virtual environment!
    pause
    exit /b 1
)

echo [OK] Virtual environment da kich hoat
echo.

REM Check if packages are installed
echo [INFO] Kiem tra cac thu vien...
python -c "import torch, cv2, facenet_pytorch" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Cac thu vien chua duoc cai dat day du!
    echo [INFO] Dang cai dat thu vien tu requirements.txt...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Loi khi cai dat thu vien!
        pause
        exit /b 1
    )
    echo.
    echo [OK] Cac thu vien da duoc cai dat
    echo.
)

echo [OK] Tat ca thu vien da san sang
echo.

REM Create data directories if not exist
if not exist "data\" mkdir data
if not exist "data\database\" mkdir data\database
if not exist "data\models\" mkdir data\models
if not exist "data\attendance_logs\" mkdir data\attendance_logs
if not exist "data\reports\" mkdir data\reports
if not exist "data\temp\" mkdir data\temp

echo ============================================================
echo    KHOI DONG UNG DUNG...
echo ============================================================
echo.

REM Run the application
python main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Ung dung gap loi!
    echo Vui long kiem tra log file: data\system.log
    pause
    exit /b 1
)

echo.
echo [INFO] Ung dung da dong
pause
