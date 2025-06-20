from sentence_transformers import SentenceTransformer
import numpy as np
from scipy.spatial.distance import cosine
from typing import List, Tuple
import json

class SemanticSearchService:
    def __init__(self):
        # Load a pre-trained model optimized for code
        # This model works well for code and technical text
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def create_embedding(self, text: str) -> List[float]:
        """Create embedding for a piece of text"""
        # Combine code and description for better search
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def create_snippet_embedding(self, title: str, description: str, code: str, language: str) -> List[float]:
        """Create embedding for a code snippet"""
        # Combine all relevant text for embedding
        combined_text = f"{title}\n{description}\n{language}\n{code}"
        return self.create_embedding(combined_text)
    
    def calculate_similarity(self, query_embedding: List[float], snippet_embedding: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        # Convert to numpy arrays
        query_vec = np.array(query_embedding)
        snippet_vec = np.array(snippet_embedding)
        
        # Calculate cosine similarity (1 - cosine distance)
        similarity = 1 - cosine(query_vec, snippet_vec)
        return float(similarity)
    
    def search_snippets(self, query: str, snippets_with_embeddings: List[Tuple], limit: int = 10) -> List[Tuple]:
        """
        Search snippets using semantic similarity
        
        Args:
            query: Search query
            snippets_with_embeddings: List of (snippet, embedding) tuples
            limit: Maximum number of results
            
        Returns:
            List of (snippet, similarity_score) tuples sorted by similarity
        """
        if not snippets_with_embeddings:
            return []
            
        # Create embedding for the search query
        query_embedding = self.create_embedding(query)
        
        # Calculate similarities
        results = []
        for snippet, embedding in snippets_with_embeddings:
            if embedding:  # Make sure embedding exists
                similarity = self.calculate_similarity(query_embedding, embedding)
                results.append((snippet, similarity))
        
        # Sort by similarity (highest first) and limit results
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

# Global instance
search_service = SemanticSearchService()