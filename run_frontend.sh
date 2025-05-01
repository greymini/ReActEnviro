#!/bin/bash

# This script runs the frontend application

# Get the absolute path of the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the frontend directory
cd "$SCRIPT_DIR/frontend"

# Run the frontend
npm start 