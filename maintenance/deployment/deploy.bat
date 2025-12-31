@echo off
REM Windows deployment script for POS System
REM Usage: Run as Administrator

echo =========================================
echo POS System Windows Deployment
echo =========================================

REM Configuration
set APP_DIR=C:\possystem
set VENV_DIR=%APP_DIR%\venv

echo Step 1: Creating application directory...
if not exist "%APP_DIR%" mkdir "%APP_DIR%"
if not exist "%APP_DIR%\logs" mkdir "%APP_DIR%\logs"
if not exist "%APP_DIR%\staticfiles" mkdir "%APP_DIR%\staticfiles"
if not exist "%APP_DIR%\media" mkdir "%APP_DIR%\media"

echo Step 2: Creating virtual environment...
python -m venv "%VENV_DIR%"
call "%VENV_DIR%\Scripts\activate.bat"

echo Step 3: Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

echo Step 4: Running migrations...
python manage.py migrate --noinput

echo Step 5: Collecting static files...
python manage.py collectstatic --noinput

echo Step 6: Creating Windows Service...
echo To run as a service, install NSSM (Non-Sucking Service Manager):
echo 1. Download NSSM from https://nssm.cc/download
echo 2. Run: nssm install possystem "%VENV_DIR%\Scripts\python.exe" "manage.py runserver 0.0.0.0:8000"
echo 3. Or use: waitress-serve --listen=*:8000 possystem.wsgi:application

echo.
echo =========================================
echo Deployment Complete!
echo =========================================
echo.
echo To start the server:
echo   1. Activate venv: %VENV_DIR%\Scripts\activate.bat
echo   2. Run server: python manage.py runserver 0.0.0.0:8000
echo.
echo For production, install waitress:
echo   pip install waitress
echo   waitress-serve --listen=*:8000 possystem.wsgi:application
echo.

pause
