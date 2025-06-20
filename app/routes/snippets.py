from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json

from app.services.database import get_db, SnippetDB
from app.schemas.snippet import Snippet, SnippetCreate, SnippetUpdate, SearchRequest, SearchResponse
from app.services.search import search_service

router = APIRouter()

# Helper function to convert DB model to Pydantic model
def db_to_pydantic(db_snippet: SnippetDB, similarity: float = None) -> Snippet:
    return Snippet(
        id=db_snippet.id,
        title=db_snippet.title,
        description=db_snippet.description,
        code=db_snippet.code,
        language=db_snippet.language,
        tags=db_snippet.tags or [],
        created_at=db_snippet.created_at,
        similarity=similarity
    )

@router.post("/snippets", response_model=Snippet, status_code=status.HTTP_201_CREATED)
async def create_snippet(snippet: SnippetCreate, db: Session = Depends(get_db)):
    """Create a new code snippet"""
    
    # Create embedding for the snippet
    embedding = search_service.create_snippet_embedding(
        title=snippet.title,
        description=snippet.description or "",
        code=snippet.code,
        language=snippet.language
    )
    
    # Create database record
    db_snippet = SnippetDB(
        title=snippet.title,
        description=snippet.description,
        code=snippet.code,
        language=snippet.language,
        tags=snippet.tags,
        embedding=embedding
    )
    
    db.add(db_snippet)
    db.commit()
    db.refresh(db_snippet)
    
    return db_to_pydantic(db_snippet)

@router.get("/snippets", response_model=List[Snippet])
async def get_all_snippets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all code snippets"""
    snippets = db.query(SnippetDB).offset(skip).limit(limit).all()
    return [db_to_pydantic(snippet) for snippet in snippets]

@router.get("/snippets/{snippet_id}", response_model=Snippet)
async def get_snippet(snippet_id: int, db: Session = Depends(get_db)):
    """Get a specific code snippet by ID"""
    snippet = db.query(SnippetDB).filter(SnippetDB.id == snippet_id).first()
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    return db_to_pydantic(snippet)

@router.put("/snippets/{snippet_id}", response_model=Snippet)
async def update_snippet(snippet_id: int, snippet_update: SnippetUpdate, db: Session = Depends(get_db)):
    """Update a code snippet"""
    snippet = db.query(SnippetDB).filter(SnippetDB.id == snippet_id).first()
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    
    # Update fields that were provided
    update_data = snippet_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(snippet, field, value)
    
    # Recreate embedding if content changed
    if any(field in update_data for field in ['title', 'description', 'code', 'language']):
        embedding = search_service.create_snippet_embedding(
            title=snippet.title,
            description=snippet.description or "",
            code=snippet.code,
            language=snippet.language
        )
        snippet.embedding = embedding
    
    db.commit()
    db.refresh(snippet)
    
    return db_to_pydantic(snippet)

@router.delete("/snippets/{snippet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_snippet(snippet_id: int, db: Session = Depends(get_db)):
    """Delete a code snippet"""
    snippet = db.query(SnippetDB).filter(SnippetDB.id == snippet_id).first()
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    
    db.delete(snippet)
    db.commit()

@router.post("/search", response_model=SearchResponse)
async def search_snippets(search_request: SearchRequest, db: Session = Depends(get_db)):
    """Search code snippets using semantic similarity"""
    
    # Get all snippets with embeddings
    all_snippets = db.query(SnippetDB).all()
    
    if not all_snippets:
        return SearchResponse(snippets=[], total_count=0, query=search_request.query)
    
    # Prepare snippets with embeddings for search
    snippets_with_embeddings = [
        (snippet, snippet.embedding) 
        for snippet in all_snippets 
        if snippet.embedding  # Only include snippets with embeddings
    ]
    
    # Perform semantic search
    search_results = search_service.search_snippets(
        query=search_request.query,
        snippets_with_embeddings=snippets_with_embeddings,
        limit=search_request.limit
    )
    
    # Convert to response format
    result_snippets = [
        db_to_pydantic(snippet, similarity=similarity)
        for snippet, similarity in search_results
    ]
    
    return SearchResponse(
        snippets=result_snippets,
        total_count=len(result_snippets),
        query=search_request.query
    )

@router.get("/languages", response_model=List[str])
async def get_available_languages(db: Session = Depends(get_db)):
    """Get list of available programming languages"""
    languages = db.query(SnippetDB.language).distinct().all()
    return [lang[0] for lang in languages if lang[0]]