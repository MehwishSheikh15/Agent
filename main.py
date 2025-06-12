from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import pytz
import sqlite3
import os
import asyncio
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv
        
# Load environment variables
load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY")
weather_key = os.getenv("WEATHER_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
def init_db():
    try:
        conn = sqlite3.connect("agent_system.db")
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0,
            priority TEXT DEFAULT 'medium',
            category TEXT DEFAULT 'general',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            reminder_time TIMESTAMP NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            agent_type TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS blog_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            content TEXT NOT NULL,
            word_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS code_snippets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            language TEXT NOT NULL,
            code TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

# Initialize database on startup
init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Multi-Agent System API...")
    yield
    # Shutdown
    logger.info("Shutting down Multi-Agent System API...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Multi-Agent System API",
    description="AI-powered multi-agent system with enhanced AI and weather features",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files for PWA
app.mount("/static", StaticFiles(directory="static"), name="static")

# Models
class TodoItem(BaseModel):
    task: str
    completed: bool = False
    priority: str = "medium"
    category: str = "general"

class ReminderItem(BaseModel):
    text: str
    datetime: str

class BlogRequest(BaseModel):
    topic: str
    length: str = "Medium"
    style: str = "informative"

class WeatherRequest(BaseModel):
    location: str

class ChatRequest(BaseModel):
    message: str

class CodeRequest(BaseModel):
    description: str
    language: str = "python"



# Helper function to get database connection
def get_db_connection():
    conn = sqlite3.connect("agent_system.db")
    conn.row_factory = sqlite3.Row
    return conn

# PWA Routes
@app.get("/manifest.json")
async def get_manifest():
    return FileResponse("static/manifest.json")

@app.get("/sw.js")
async def get_service_worker():
    return FileResponse("static/sw.js")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Routes
@app.get("/")
async def root():
    return {
        "message": "Multi-Agent System API is running",
        "version": "2.0.0",
        "status": "operational",
        "features": ["tasks", "chat", "content", "code", "weather"]
    }

# Personal Assistant Agent routes
@app.get("/todos")
async def get_todos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM todos ORDER BY created_at DESC")
        todos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"todos": todos}
    except Exception as e:
        logger.error(f"Error fetching todos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/todos/add")
async def add_todo(todo: TodoItem):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO todos (task, completed, priority, category) VALUES (?, ?, ?, ?)",
            (todo.task, todo.completed, todo.priority, todo.category)
        )
        conn.commit()
        todo_id = cursor.lastrowid
        conn.close()
        return {
            "id": todo_id,
            "task": todo.task,
            "completed": todo.completed,
            "priority": todo.priority,
            "category": todo.category
        }
    except Exception as e:
        logger.error(f"Error adding todo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/todos/{todo_id}")
async def update_todo(todo_id: int, completed: bool):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE todos SET completed = ? WHERE id = ?", (completed, todo_id))
        conn.commit()
        conn.close()
        return {"id": todo_id, "completed": completed}
    except Exception as e:
        logger.error(f"Error updating todo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        conn.commit()
        conn.close()
        return {"message": "Todo deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting todo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Content Creator Agent routes
@app.post("/generate/blog")
async def generate_blog(request: BlogRequest):
    try:
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        if gemini_key and gemini_key != "your_gemini_api_key_here":
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                
                # Map length to word count
                length_map = {
                    "Short": "300-400 words",
                    "Medium": "600-800 words", 
                    "Long": "1200-1500 words"
                }
                word_count_instruction = length_map.get(request.length, "600-800 words")
                
                # Create style-specific prompts
                style_prompts = {
                    "informative": f"Write a comprehensive, informative blog post about {request.topic}. Use a professional tone with clear explanations and factual information.",
                    "casual": f"Write a casual, friendly blog post about {request.topic}. Use a conversational tone as if talking to a friend.",
                    "professional": f"Write a professional, business-oriented blog post about {request.topic}. Use formal language suitable for corporate audiences.",
                    "creative": f"Write a creative, engaging blog post about {request.topic}. Use storytelling elements and imaginative language."
                }
                
                prompt = f"""
                {style_prompts.get(request.style, style_prompts['informative'])}
                
                Requirements:
                - Length: {word_count_instruction}
                - Include a compelling title
                - Use proper headings and structure with markdown formatting
                - Make it engaging and well-researched
                - Include practical insights or actionable advice
                - Use bullet points and numbered lists where appropriate
                - Add a conclusion that summarizes key points
                
                Topic: {request.topic}
                
                Please format the response with proper markdown headers (# ## ###) and structure.
                """
                
                response = model.generate_content(prompt)
                content = response.text
                word_count = len(content.split())
                
                # Save to database
                conn = get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute(
                    "INSERT INTO blog_content (topic, content, word_count) VALUES (?, ?, ?)",
                    (request.topic, content, word_count)
                )
                
                conn.commit()
                conn.close()
                
                return {
                    "content": content, 
                    "topic": request.topic, 
                    "length": request.length, 
                    "style": request.style,
                    "word_count": word_count,
                    "model": "Gemini 2.0 Flash"
                }
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                # Fallback content
                fallback_content = f"""
# {request.topic}

This is a sample blog post about {request.topic}. 

## Introduction

{request.topic} is an important topic that deserves attention and discussion.

## Main Content

Here we would explore the various aspects of {request.topic}, providing insights and valuable information.

## Conclusion

In conclusion, {request.topic} offers many opportunities for learning and growth.

*Note: Configure GEMINI_API_KEY for AI-generated content.*
                """
                
                return {
                    "content": fallback_content,
                    "topic": request.topic,
                    "length": request.length,
                    "style": request.style,
                    "word_count": len(fallback_content.split()),
                    "note": "Fallback content - Configure Gemini API for AI generation"
                }
        else:
            # Fallback when no API key
            fallback_content = f"""
# {request.topic}

This is a sample blog post about {request.topic}. 

Configure GEMINI_API_KEY in your .env file for AI-generated content.

## Sample Content

Your AI-generated blog post would appear here with proper formatting, engaging content, and professional structure.

*Generated by Gemini 2.0 Flash when properly configured.*
            """
            
            return {
                "content": fallback_content,
                "topic": request.topic,
                "length": request.length,
                "style": request.style,
                "word_count": len(fallback_content.split()),
                "note": "Configure GEMINI_API_KEY for AI content generation"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/blogs")
async def get_blogs():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM blog_content ORDER BY created_at DESC")
        blogs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"blogs": blogs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced Weather Agent routes
@app.post("/weather")
async def get_weather(request: WeatherRequest):
    try:
        weather_key = os.getenv("WEATHER_API_KEY")
        
        if weather_key and weather_key != "your_weather_api_key_here":
            import requests
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": request.location,
                "appid": weather_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Get weather icon
                weather_icons = {
                    "clear": "☀️",
                    "clouds": "☁️",
                    "rain": "🌧️",
                    "drizzle": "🌦️",
                    "thunderstorm": "⛈️",
                    "snow": "❄️",
                    "mist": "🌫️",
                    "fog": "🌫️",
                    "haze": "🌫️"
                }
                
                weather_main = data['weather'][0]['main'].lower()
                icon = weather_icons.get(weather_main, "🌤️")
                
                return {
                    "location": f"{data['name']}, {data['sys']['country']}",
                    "temperature": round(data['main']['temp']),
                    "feels_like": round(data['main']['feels_like']),
                    "description": data['weather'][0]['description'].title(),
                    "humidity": data['main']['humidity'],
                    "pressure": data['main']['pressure'],
                    "wind_speed": round(data['wind']['speed'] * 3.6, 1),
                    "wind_direction": data['wind'].get('deg', 0),
                    "visibility": data.get('visibility', 0) / 1000,
                    "icon": icon,
                    "sunrise": datetime.fromtimestamp(data['sys']['sunrise']).strftime("%H:%M"),
                    "sunset": datetime.fromtimestamp(data['sys']['sunset']).strftime("%H:%M")
                }
            else:
                return {"error": "Location not found"}
        else:
            return {
                "error": "Weather API key not configured",
                "message": "Please set WEATHER_API_KEY in your .env file"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/weather/forecast/{location}")
async def get_forecast(location: str):
    try:
        weather_key = os.getenv("WEATHER_API_KEY")
        
        if weather_key and weather_key != "your_weather_api_key_here":
            import requests
            url = "http://api.openweathermap.org/data/2.5/forecast"
            params = {
                "q": location,
                "appid": weather_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Process forecast data (API returns 3-hour intervals)
                daily_forecasts = {}
                
                for item in data['list']:
                    date = datetime.fromtimestamp(item['dt']).date()
                    
                    if date not in daily_forecasts:
                        daily_forecasts[date] = {
                            "date": date.strftime("%Y-%m-%d"),
                            "day": date.strftime("%A"),
                            "temperatures": [],
                            "descriptions": [],
                            "humidity": [],
                            "wind_speeds": [],
                            "precipitation": 0
                        }
                    
                    daily_forecasts[date]["temperatures"].append(item['main']['temp'])
                    daily_forecasts[date]["descriptions"].append(item['weather'][0]['description'])
                    daily_forecasts[date]["humidity"].append(item['main']['humidity'])
                    daily_forecasts[date]["wind_speeds"].append(item['wind']['speed'] * 3.6)
                    
                    # Check for precipitation
                    if 'rain' in item:
                        daily_forecasts[date]["precipitation"] += item['rain'].get('3h', 0)
                    if 'snow' in item:
                        daily_forecasts[date]["precipitation"] += item['snow'].get('3h', 0)
                
                # Create final forecast
                forecast = []
                for date, data_day in list(daily_forecasts.items())[:5]:  # 5 days
                    weather_icons = {
                        "clear": "☀️",
                        "clouds": "☁️",
                        "rain": "🌧️",
                        "drizzle": "🌦️",
                        "thunderstorm": "⛈️",
                        "snow": "❄️",
                        "mist": "🌫️",
                        "fog": "🌫️",
                        "haze": "🌫️"
                    }
                    
                    most_common_desc = max(set(data_day["descriptions"]), key=data_day["descriptions"].count)
                    icon = weather_icons.get(most_common_desc.split()[0].lower(), "🌤️")
                    
                    forecast.append({
                        "date": data_day["date"],
                        "day": data_day["day"],
                        "high_temperature": round(max(data_day["temperatures"])),
                        "low_temperature": round(min(data_day["temperatures"])),
                        "description": most_common_desc.title(),
                        "icon": icon,
                        "humidity": round(sum(data_day["humidity"]) / len(data_day["humidity"])),
                        "wind_speed": round(sum(data_day["wind_speeds"]) / len(data_day["wind_speeds"]), 1),
                        "precipitation_chance": min(100, round(data_day["precipitation"] * 10))
                    })
                
                return {
                    "location": f"{data['city']['name']}, {data['city']['country']}",
                    "forecast": forecast,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": "Location not found"}
        else:
            return {
                "error": "Weather API key not configured",
                "message": "Please set WEATHER_API_KEY in your .env file"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chatbot Agent routes
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Check if Gemini API key is available
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        if gemini_key and gemini_key != "your_gemini_api_key_here":
            # Use Gemini API
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                
                response = model.generate_content(f"""
                You are a helpful AI assistant. Respond to this message in a friendly and helpful way:
                
                User: {request.message}
                
                Keep your response concise but informative.
                """)
                
                bot_response = response.text
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                bot_response = f"I'm here to help! You asked: '{request.message}'. While I'm having trouble with my AI features right now, I can still assist you with basic tasks. Try using the other features in the system!"
        else:
            # Fallback response
            bot_response = f"Hello! You said: '{request.message}'. I'm your AI assistant, but I need a Gemini API key to provide intelligent responses. Please configure GEMINI_API_KEY in your .env file."
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (user_message, bot_response) VALUES (?, ?)",
            (request.message, bot_response)
        )
        conn.commit()
        conn.close()
        
        return {
            "user_message": request.message,
            "bot_response": bot_response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/history")
async def get_chat_history():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chat_history ORDER BY timestamp DESC LIMIT 20")
        history = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"history": list(reversed(history))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Code Generator Agent routes
@app.post("/code/generate")
async def generate_code(request: CodeRequest):
    try:
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        if gemini_key and gemini_key != "your_gemini_api_key_here":
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                
                prompt = f"""
                Generate {request.language} code for the following requirement:
                {request.description}
                
                Requirements:
                - Write clean, well-commented code
                - Include error handling where appropriate
                - Add example usage if applicable
                - Follow best practices for {request.language}
                - Make the code production-ready
                - Include docstrings/comments explaining the functionality
                - Use modern {request.language} features and conventions
                
                Provide only the code with comments, no additional explanation outside the code.
                """
                
                response = model.generate_content(prompt)
                code = response.text
                
                # Generate explanation
                explanation_prompt = f"""
                Explain this {request.language} code in simple terms:
                
                {code}
                
                Provide:
                1. What the code does (main purpose)
                2. How it works (step by step explanation)
                3. Key features or concepts used
                4. When and why to use this code
                5. Any important notes about the implementation
                
                Make the explanation clear and educational for developers of all levels.
                """
                
                explanation_response = model.generate_content(explanation_prompt)
                explanation = explanation_response.text
                
                # Save to database
                conn = get_db_connection()
                cursor = conn.cursor()
                
                title = request.description[:50] + "..." if len(request.description) > 50 else request.description
                
                cursor.execute(
                    "INSERT INTO code_snippets (title, language, code, description) VALUES (?, ?, ?, ?)",
                    (title, request.language, code, explanation)
                )
                
                conn.commit()
                conn.close()
                
                return {
                    "code": code,
                    "language": request.language,
                    "description": request.description,
                    "explanation": explanation,
                    "title": title,
                    "model": "Gemini 2.0 Flash"
                }
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                # Fallback code
                fallback_code = f"""
# {request.description}
# This is a sample {request.language} code snippet

def sample_function():
    '''
    Sample function for {request.description}
    Configure GEMINI_API_KEY for AI-generated code
    '''
    print("Configure Gemini API for code generation")
    return "Sample output"

# Example usage
if __name__ == "__main__":
    result = sample_function()
    print(result)
                """
                
                return {
                    "code": fallback_code,
                    "language": request.language,
                    "description": request.description,
                    "explanation": "This is a sample code snippet. Configure GEMINI_API_KEY for AI-generated code.",
                    "title": title,
                    "note": "Fallback code - Configure Gemini API for AI generation"
                }
        else:
            # Fallback when no API key
            fallback_code = f"""
# {request.description}
# Configure GEMINI_API_KEY for AI-generated code

print("Configure Gemini API key in .env file")
print("Then you'll get AI-generated code here!")
            """
            
            return {
                "code": fallback_code,
                "language": request.language,
                "description": request.description,
                "explanation": "Configure GEMINI_API_KEY in your .env file for AI-generated code.",
                "title": title,
                "note": "Configure GEMINI_API_KEY for AI code generation"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/code/snippets")
async def get_code_snippets():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM code_snippets ORDER BY created_at DESC")
        snippets = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"snippets": snippets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced E-commerce Web Developer Agent routes



if __name__ == "__main__":
    try:
        logger.info("Starting server on http://0.0.0.0:8000")
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
