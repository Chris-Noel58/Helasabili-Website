@echo off
REM NCHSM Kikuyu Campus - Installation Script for Windows

echo.
echo ==========================================
echo NCHSM Kikuyu Campus - Installation Script
echo ==========================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)
echo Python found
echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
echo Pip upgraded
echo.

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt
echo Dependencies installed
echo.

REM Create .env file
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo .env file created (edit with your settings)
) else (
    echo .env file already exists
)
echo.

REM Create directories
echo Creating directories...
if not exist "media\courses" mkdir media\courses
if not exist "media\blog" mkdir media\blog
if not exist "media\gallery" mkdir media\gallery
if not exist "media\testimonials" mkdir media\testimonials
if not exist "media\admin" mkdir media\admin
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js
if not exist "static\images" mkdir static\images
if not exist "logs" mkdir logs
if not exist "templates\website" mkdir templates\website
if not exist "templates\dashboard" mkdir templates\dashboard
if not exist "templates\partials" mkdir templates\partials
if not exist "templates\errors" mkdir templates\errors
echo Directories created
echo.

REM Run migrations
echo Running database migrations...
python manage.py makemigrations
python manage.py migrate
echo Database migrations completed
echo.

REM Collect static files
echo Collecting static files...
python manage.py collectstatic --noinput >nul 2>&1
echo Static files collected
echo.

REM Create superuser
echo.
echo ==========================================
echo Create Admin User
echo ==========================================
echo Please enter admin credentials:
python manage.py createsuperuser
echo.

echo ==========================================
echo Installation Complete!
echo ==========================================
echo.
echo To start the development server, run:
echo   venv\Scripts\activate.bat
echo   python manage.py runserver
echo.
echo Then access:
echo   Website: http://localhost:8000
echo   Dashboard: http://localhost:8000/dashboard/login/
echo   Django Admin: http://localhost:8000/admin/
echo.
echo For more information, see QUICKSTART.md
echo.
pause
