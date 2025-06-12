#!/bin/bash

echo "Starting Multi-Agent System..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start the API server in background
echo "Starting API server..."
python main.py &
API_PID=$!

# Wait a moment for the API to start
sleep 3

# Start Streamlit
echo "Starting Streamlit UI..."
streamlit run app.py

# Kill the API server when Streamlit exits
kill $API_PID
