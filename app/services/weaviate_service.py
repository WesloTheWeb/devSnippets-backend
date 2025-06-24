import weaviate
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WeaviateService:
    """
    Weaviate service handles all vector database operations.
    Think of this like a specialized API client for vector search.
    """
    
    def __init__(self):
        # Get credentials from environment variables
        self.weaviate_url = os.getenv("WEAVIATE_URL")
        self.weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
        
        if not self.weaviate_url or not self.weaviate_api_key:
            raise ValueError("Weaviate credentials not found in environment variables")
        
        # Create connection to Weaviate cloud
        self.client = weaviate.Client(
            url=self.weaviate_url,
            auth_client_secret=weaviate.AuthApiKey(api_key=self.weaviate_api_key)
        )
        
        # Ensure our schema exists
        self._create_schema()
    
    def _create_schema(self):
        """
        Create the schema (like creating a table in PostgreSQL).
        This defines what data structure Weaviate expects.
        """
        schema = {
            "class": "CodeSnippet",           # Like a table name
            "vectorizer": "none",             # We provide our own vectors (from sentence-transformers)
            "properties": [                   # Like table columns
                {
                    "name": "snippet_id",     # References PostgreSQL ID
                    "dataType": ["string"],
                    "description": "ID from PostgreSQL database"
                },
                {
                    "name": "title",
                    "dataType": ["string"],
                    "description": "Snippet title for filtering"
                },
                {
                    "name": "language",
                    "dataType": ["string"], 
                    "description": "Programming language"
                },
                {
                    "name": "description",
                    "dataType": ["text"],
                    "description": "Snippet description"
                }
            ]
        }
        
        try:
            # Check if schema already exists
            existing_schema = self.client.schema.get()
            class_names = [cls["class"] for cls in existing_schema["classes"]]
            
            if "CodeSnippet" not in class_names:
                self.client.schema.create_class(schema)
                print("✅ Created Weaviate schema for CodeSnippet")
            else:
                print("✅ Weaviate schema already exists")
                
        except Exception as e:
            print(f"❌ Error creating Weaviate schema: {e}")
    
    def store_snippet_vector(self, snippet_id: str, embedding: List[float], title: str, 
                           language: str, description: str = "") -> bool:
        """
        Store a code snippet's vector in Weaviate.
        This is like INSERT INTO but for vectors.
        """
        try:
            # Convert snippet_id to string for consistency
            snippet_id_str = str(snippet_id)
            
            # Create the data object
            data_object = {
                "snippet_id": snippet_id_str,
                "title": title,
                "language": language,
                "description": description
            }
            
            # Store in Weaviate with the vector
            result = self.client.data_object.create(
                data_object=data_object,
                class_name="CodeSnippet",
                vector=embedding  # This is the magic - the actual ML embedding
            )
            
            print(f"✅ Stored snippet {snippet_id} in Weaviate")
            return True
            
        except Exception as e:
            print(f"❌ Error storing snippet {snippet_id} in Weaviate: {e}")
            return False
    
    def search_similar_snippets(self, query_vector: List[float], limit: int = 10) -> List[Dict]:
        """
        Search for similar vectors in Weaviate.
        This is the fast vector search that makes everything worth it.
        """
        try:
            # Perform vector similarity search
            result = (
                self.client.query
                .get("CodeSnippet", ["snippet_id", "title", "language", "description"])
                .with_near_vector({
                    "vector": query_vector,
                    "certainty": 0.6  # Minimum similarity threshold (0.6 = 60% similar)
                })
                .with_limit(limit)
                .with_additional(["certainty"])  # Include similarity score
                .do()
            )
            
            # Extract results
            if "data" in result and "Get" in result["data"] and "CodeSnippet" in result["data"]["Get"]:
                snippets = result["data"]["Get"]["CodeSnippet"]
                
                # Format results for easier use
                formatted_results = []
                for snippet in snippets:
                    formatted_results.append({
                        "snippet_id": snippet["snippet_id"],
                        "title": snippet["title"],
                        "language": snippet["language"], 
                        "description": snippet["description"],
                        "similarity": snippet["_additional"]["certainty"]  # Weaviate's similarity score
                    })
                
                print(f"✅ Found {len(formatted_results)} similar snippets in Weaviate")
                return formatted_results
            else:
                print("No results found in Weaviate")
                return []
                
        except Exception as e:
            print(f"❌ Error searching Weaviate: {e}")
            return []
    
    def delete_snippet_vector(self, snippet_id: str) -> bool:
        """
        Delete a snippet's vector from Weaviate.
        Used when deleting snippets from PostgreSQL.
        """
        try:
            # Find the object by snippet_id
            result = (
                self.client.query
                .get("CodeSnippet", ["snippet_id"])
                .with_where({
                    "path": ["snippet_id"],
                    "operator": "Equal",
                    "valueString": str(snippet_id)
                })
                .with_additional(["id"])
                .do()
            )
            
            if "data" in result and "Get" in result["data"] and "CodeSnippet" in result["data"]["Get"]:
                snippets = result["data"]["Get"]["CodeSnippet"]
                for snippet in snippets:
                    weaviate_id = snippet["_additional"]["id"]
                    self.client.data_object.delete(weaviate_id)
                    print(f"✅ Deleted snippet {snippet_id} from Weaviate")
                return True
            else:
                print(f"Snippet {snippet_id} not found in Weaviate")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting snippet {snippet_id} from Weaviate: {e}")
            return False

# Create global instance (like a singleton)
weaviate_service = WeaviateService()