import os
import shutil

def setup_environment():
    print("🔧 Setting up Multi-Agent System...")
    print("=" * 40)
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✅ Created .env file from template")
        else:
            with open('.env', 'w') as f:
                f.write("""# Gemini API Key (Required for AI features)
# Get your free key from: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Weather API Key (Optional - for real weather data)
# Get free key from: https://openweathermap.org/api
WEATHER_API_KEY=your_weather_api_key_here
""")
            print("✅ Created .env file")
    
    print("\n🔑 API Keys Setup:")
    print("-" * 20)
    print("1. Get Gemini API key: https://aistudio.google.com/app/apikey")
    print("2. Get Weather API key: https://openweathermap.org/api")
    print("3. Edit the .env file and add your keys")
    
    print("\n🚀 To run the system:")
    print("-" * 20)
    print("1. pip install -r requirements.txt")
    print("2. python main.py (start API server)")
    print("3. streamlit run app.py (start UI)")
    
    print("\n📱 Mobile Installation:")
    print("-" * 20)
    print("1. Open the app in your mobile browser")
    print("2. Tap 'Add to Home Screen' in browser menu")
    print("3. Enjoy the mobile app experience!")

if __name__ == "__main__":
    setup_environment()
