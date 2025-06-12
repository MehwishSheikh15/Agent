from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TodoItem(BaseModel):
    id: Optional[int] = None
    task: str
    completed: bool = False
    created_at: Optional[datetime] = None

class ReminderItem(BaseModel):
    id: Optional[int] = None
    text: str
    reminder_time: datetime
    created_at: Optional[datetime] = None

class TaskHistoryItem(BaseModel):
    id: Optional[int] = None
    action: str
    timestamp: Optional[datetime] = None

class BlogContent(BaseModel):
    id: Optional[int] = None
    topic: str
    content: str
    created_at: Optional[datetime] = None

class NewsArticle(BaseModel):
    title: str
    summary: str
    source: str
    url: Optional[str] = None
    published_at: Optional[datetime] = None

class NewsResponse(BaseModel):
    category: str
    articles: List[NewsArticle]
    timestamp: datetime

class GenerateBlogRequest(BaseModel):
    topic: str
    length: str = Field(default="Medium", description="Length of the blog content")

class NewsAnalysisRequest(BaseModel):
    query: str
