#!/bin/bash

# Exit on any error
set -e

DIRECTORY=".venv"

# Remove existing virtual environment if it exists
if [ -d "$DIRECTORY" ]; then
    echo "🗑️  Removing existing $DIRECTORY"
    rm -rf $DIRECTORY
fi

echo "🔧 Creating new virtual environment..."
python3 -m venv $DIRECTORY

# Activate virtual environment
echo "🔌 Activating virtual environment"
source $DIRECTORY/bin/activate

# Show Python version and location
echo "🐍 Python version and location:"
which python
python3 --version

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip3 install --upgrade pip

# Install the package in development mode with all dependencies
echo "📦 Installing packages"
pip3 install -r ./requirements.txt