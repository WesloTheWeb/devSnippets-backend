# generate_embeddings.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.database import SnippetDB
from app.services.search import search_service

# Load environment variables
load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def generate_missing_embeddings():
    """Generate embeddings for snippets that don't have them"""
    db = SessionLocal()
    try:
        # Find snippets without embeddings
        snippets_without_embeddings = db.query(SnippetDB).filter(
            SnippetDB.embedding.is_(None)
        ).all()
        
        print(f"Found {len(snippets_without_embeddings)} snippets without embeddings")
        
        for snippet in snippets_without_embeddings:
            print(f"Generating embedding for: {snippet.title}")
            
            # Create embedding
            embedding = search_service.create_snippet_embedding(
                title=snippet.title,
                description=snippet.description or "",
                code=snippet.code,
                language=snippet.language
            )
            
            # Update the snippet
            snippet.embedding = embedding
            db.commit()
            
            print(f"✅ Generated embedding for: {snippet.title}")
        
        print(f"🎉 Successfully generated embeddings for {len(snippets_without_embeddings)} snippets!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_missing_embeddings()