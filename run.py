import subprocess
import sys
import time
import os
from threading import Thread

def run_api_server():
    """Run the FastAPI server"""
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("API server stopped")
    except Exception as e:
        print(f"API server error: {e}")

def run_streamlit():
    """Run the Streamlit app"""
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("Streamlit app stopped")
    except Exception as e:
        print(f"Streamlit error: {e}")

def main():
    print("🚀 Starting Multi-Agent System...")
    print("=" * 40)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  .env file not found!")
        print("Run: python setup.py")
        return
    
    print("🔧 Starting API server...")
    api_thread = Thread(target=run_api_server, daemon=True)
    api_thread.start()
    
    # Wait for API server to start
    time.sleep(3)
    
    print("🎨 Starting Streamlit UI...")
    print("🌐 Opening browser at http://localhost:8501")
    
    try:
        run_streamlit()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")

if __name__ == "__main__":
    main()
