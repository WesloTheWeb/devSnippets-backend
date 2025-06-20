from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Base snippet schema
class SnippetBase(BaseModel):
    title: str
    description: Optional[str] = None
    code: str
    language: str
    tags: List[str] = []

# For creating snippets (POST)
class SnippetCreate(SnippetBase):
    pass

# For updating snippets (PUT)
class SnippetUpdate(SnippetBase):
    title: Optional[str] = None
    code: Optional[str] = None
    language: Optional[str] = None

# For search requests
class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10

# For API responses
class Snippet(SnippetBase):
    id: int
    created_at: datetime
    similarity: Optional[float] = None  # For search results
    
    class Config:
        from_attributes = True  # For SQLAlchemy compatibility

# For search responses  
class SearchResponse(BaseModel):
    snippets: List[Snippet]
    total_count: int
    query: str