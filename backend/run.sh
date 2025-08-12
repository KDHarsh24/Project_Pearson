#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define the virtual environment directory.
VENV_DIR="venv"

# Check if the virtual environment directory exists.
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv $VENV_DIR
fi

# Activate the virtual environment.
source $VENV_DIR/bin/activate

# Install the required dependencies.
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Run the FastAPI application.
echo "Starting the FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8000
