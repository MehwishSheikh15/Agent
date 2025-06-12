import json
from datetime import datetime
import pytz

def format_datetime(dt_str, format_str="%Y-%m-%d %H:%M:%S"):
    """Format datetime string to desired format"""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime(format_str)
    except:
        return dt_str

def get_current_timestamp():
    """Get current timestamp in ISO format"""
    return datetime.now(pytz.UTC).isoformat()

def save_to_json(data, filename):
    """Save data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def load_from_json(filename):
    """Load data from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except:
        return None

def truncate_text(text, max_length=100):
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."