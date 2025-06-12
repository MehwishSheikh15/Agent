#!/bin/bash

echo "Installing Multi-Agent System..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "Python found. Installing dependencies..."

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Failed to install dependencies."
    exit 1
fi

echo
echo "Installation completed successfully!"
echo
echo "To run the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start the API server: python main.py"
echo "3. In another terminal, start the UI: streamlit run app.py"
echo

# Make the script executable
chmod +x run.sh
