# migrate_to_weaviate.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.database import SnippetDB
from app.services.weaviate_service import weaviate_service

# Load environment variables
load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def migrate_snippets_to_weaviate():
    """Migrate all PostgreSQL snippets to Weaviate"""
    db = SessionLocal()
    try:
        # Get all snippets with embeddings
        snippets = db.query(SnippetDB).filter(
            SnippetDB.embedding.isnot(None)
        ).all()
        
        print(f"Found {len(snippets)} snippets to migrate to Weaviate")
        
        success_count = 0
        for snippet in snippets:
            print(f"Migrating: {snippet.title}")
            
            # Store in Weaviate
            success = weaviate_service.store_snippet_vector(
                snippet_id=str(snippet.id),
                embedding=snippet.embedding,
                title=snippet.title,
                language=snippet.language,
                description=snippet.description or ""
            )
            
            if success:
                success_count += 1
                print(f"✅ Migrated: {snippet.title}")
            else:
                print(f"❌ Failed: {snippet.title}")
        
        print(f"🎉 Successfully migrated {success_count}/{len(snippets)} snippets to Weaviate!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_snippets_to_weaviate()