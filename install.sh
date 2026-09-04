#!/bin/bash

# NCHSM Kikuyu Campus - Installation Script
# This script automates the setup process for development

set -e

echo "=========================================="
echo "NCHSM Kikuyu Campus - Installation Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✓ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
echo "✓ Pip upgraded"
echo ""

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created (edit with your settings)"
else
    echo "✓ .env file already exists"
fi
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p media/courses media/blog media/gallery media/testimonials media/admin
mkdir -p static/css static/js static/images
mkdir -p logs
mkdir -p templates/website templates/dashboard templates/partials templates/errors
echo "✓ Directories created"
echo ""

# Run migrations
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate
echo "✓ Database migrations completed"
echo ""

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput > /dev/null 2>&1
echo "✓ Static files collected"
echo ""

# Create superuser
echo ""
echo "=========================================="
echo "Create Admin User"
echo "=========================================="
echo "Please enter admin credentials:"
python manage.py createsuperuser
echo ""

echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "To start the development server, run:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Then access:"
echo "  Website: http://localhost:8000"
echo "  Dashboard: http://localhost:8000/dashboard/login/"
echo "  Django Admin: http://localhost:8000/admin/"
echo ""
echo "For more information, see QUICKSTART.md"
echo ""
