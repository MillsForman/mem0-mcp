#!/bin/bash

# Script to start the mem0-mcp local server,
# attempting to set up and activate a virtual environment.

PROJECT_DIR="/Users/Stephen/Documents/GitHub/mem0-mcp"
VENV_DIR="${PROJECT_DIR}/.venv"
VENV_ACTIVATE_PATH="${VENV_DIR}/bin/activate"

echo "Navigating to project directory: ${PROJECT_DIR}"
cd "${PROJECT_DIR}" || { echo "Failed to navigate to project directory. Exiting."; exit 1; }

# Check if virtual environment directory exists
if [ ! -d "${VENV_DIR}" ]; then
  echo "Virtual environment not found at ${VENV_DIR}."
  echo "Attempting to create virtual environment using 'uv venv'..."
  if command -v uv &> /dev/null; then
    uv venv || { echo "Failed to create virtual environment with 'uv venv'. Please create it manually. Exiting."; exit 1; }
    echo "Virtual environment created."
    
    echo "Activating virtual environment: ${VENV_ACTIVATE_PATH}"
    source "${VENV_ACTIVATE_PATH}" || { echo "Failed to activate newly created virtual environment. Please activate manually and install dependencies. Exiting."; exit 1; }
    
    echo "Installing dependencies using 'uv pip install -e .'..."
    uv pip install -e . || { echo "Failed to install dependencies. Please install them manually. Exiting."; exit 1; }
    echo "Dependencies installed."
    
    if type deactivate &> /dev/null; then
        deactivate
    fi
  else
    printf "Error - uv not found. Please install uv or create the venv manually. Exiting.\n"
    exit 1
  fi
fi

# Attempt to activate the virtual environment for running the server
if [ -f "${VENV_ACTIVATE_PATH}" ]; then
  echo "Attempting to activate virtual environment: ${VENV_ACTIVATE_PATH}"
  source "${VENV_ACTIVATE_PATH}" || { echo "Warning: Failed to activate virtual environment. Python from current PATH will be used."; }
else
  echo "Virtual environment activation script not found at ${VENV_ACTIVATE_PATH}. Assuming Python environment is already set or in PATH."
fi

echo "Starting mem0-mcp server (main.py)..."
echo "Listening on http://127.0.0.1:8088 (Press CTRL+C to stop)"
python main.py

echo "mem0-mcp server stopped." 