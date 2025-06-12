import os
import shutil

def setup_environment():
    """Setup environment variables"""
    print("🔧 Setting up Multi-Agent System Environment")
    print("=" * 50)
    
    # Copy .env.example to .env if it doesn't exist
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✅ Created .env file from template")
        else:
            # Create .env file
            with open('.env', 'w') as f:
                f.write("""# Gemini API Key (Required for all AI agents)
# Get your key from: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Weather API Key (Required for real weather data)
# Get free key from: https://openweathermap.org/api
WEATHER_API_KEY=your_weather_api_key_here

# News API Key (Optional - for real news data)
# Get free key from: https://newsapi.org/
NEWS_API_KEY=your_news_api_key_here
""")
            print("✅ Created .env file")
    
    print("\n🔑 API Keys Setup Required:")
    print("-" * 30)
    
    # Check for API keys
    from dotenv import load_dotenv
    load_dotenv()
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    weather_key = os.getenv('WEATHER_API_KEY')
    news_key = os.getenv('NEWS_API_KEY')
    
    if not gemini_key or gemini_key == 'your_gemini_api_key_here':
        print("❌ GEMINI_API_KEY not configured")
        print("   Get your key from: https://aistudio.google.com/app/apikey")
        print("   This is REQUIRED for AI features to work")
    else:
        print("✅ GEMINI_API_KEY configured")
    
    if not weather_key or weather_key == 'your_weather_api_key_here':
        print("❌ WEATHER_API_KEY not configured")
        print("   Get your free key from: https://openweathermap.org/api")
        print("   This is REQUIRED for real weather data")
    else:
        print("✅ WEATHER_API_KEY configured")
    
    if not news_key or news_key == 'your_news_api_key_here':
        print("⚠️  NEWS_API_KEY not configured (optional)")
        print("   Get your free key from: https://newsapi.org/")
        print("   AI-generated news will be used instead")
    else:
        print("✅ NEWS_API_KEY configured")
    
    print("\n📝 Next Steps:")
    print("-" * 15)
    print("1. Edit the .env file and add your API keys")
    print("2. Run: python main.py (to start the API server)")
    print("3. Run: streamlit run app.py (to start the UI)")
    print("\nOr use the quick start scripts:")
    print("- Windows: run.bat")
    print("- Linux/Mac: ./run.sh")
    
    print("\n📱 Mobile Installation:")
    print("-" * 20)
    print("1. Open the app in your mobile browser")
    print("2. Tap browser menu and select 'Add to Home Screen'")
    print("3. The app will install as a PWA (Progressive Web App)")

if __name__ == "__main__":
    setup_environment()
