#!/usr/bin/env bash

# Usage:
#   source setup_venv.sh [--help|--deactivate]

# Exit immediately if a command exits with a non-zero status
set -e

# Define the virtual environment directory
VENV_DIR=${VENV_DIR:-"venv"}

# Function to find the correct Python command
find_python() {
    if command -v python &> /dev/null; then
        echo "python"  # Fallback to python (Windows or systems with only python)
    elif command -v python3 &> /dev/null; then
        echo "python3"  # Prefer python3 on Linux/MacOS
    else
        echo "Error: Python is not installed or not in PATH." >&2
        return 1
    fi
}

python3.13 -m venv camera_track_env
 

source camera_track_env/bin/activate

pip3 install -r requirements.txt