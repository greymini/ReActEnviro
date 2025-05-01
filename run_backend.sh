#!/bin/bash

# This script runs the backend server without needing to activate the virtual environment
# It uses the Python executable from the virtual environment directly

# Get the absolute path of the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Path to the Python interpreter in the virtual environment
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python3"

# Run the backend server
cd "$SCRIPT_DIR/backend"
"$VENV_PYTHON" main.py 