#!/bin/bash

# ASCIICam Backend Startup Script

echo "Starting ASCIICam Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade requirements (only core dependencies)
echo "Installing requirements..."
pip install --quiet fastapi "uvicorn[standard]" python-multipart aiofiles pydantic opencv-python pillow numpy

# Create necessary directories
echo "Creating directories..."
mkdir -p static/history/captures
mkdir -p static/history/processed

# Load environment variables (handle special characters properly)
if [ -f ".env" ]; then
    echo "Loading environment variables..."
    set -a  # automatically export all variables
    source .env
    set +a  # stop automatically exporting
fi

# Start the server
echo "Starting FastAPI server..."
echo "Server will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
python3 app.py
