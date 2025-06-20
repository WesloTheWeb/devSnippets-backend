from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Tuple
import json

class SemanticSearchService:
    def __init__(self):
        # Use TF-IDF instead of heavy transformer models
        # This is much lighter but still provides good search results
        self.vectorizer = TfidfVectorizer(
            max_features=5000,  # Limit vocab size
            stop_words='english',
            ngram_range=(1, 2),  # Include bigrams for better context
            min_df=1,  # Minimum document frequency
            max_df=0.95  # Maximum document frequency
        )
        self.fitted = False
        self.document_vectors = None
        self.documents = []
        
    def create_embedding(self, text: str) -> List[float]:
        """Create embedding for a piece of text using TF-IDF"""
        if not self.fitted:
            # For single documents, create a simple embedding
            temp_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            vector = temp_vectorizer.fit_transform([text])
            return vector.toarray()[0].tolist()
        else:
            # Transform using fitted vectorizer
            vector = self.vectorizer.transform([text])
            return vector.toarray()[0].tolist()
    
    def create_snippet_embedding(self, title: str, description: str, code: str, language: str) -> List[float]:
        """Create embedding for a code snippet"""
        # Combine all relevant text for embedding
        combined_text = f"{title} {description} {language} {code}"
        return self.create_embedding(combined_text)
    
    def calculate_similarity(self, query_embedding: List[float], snippet_embedding: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        # Convert to numpy arrays and reshape for sklearn
        query_vec = np.array(query_embedding).reshape(1, -1)
        snippet_vec = np.array(snippet_embedding).reshape(1, -1)
        
        # Handle case where vectors might have different lengths
        min_len = min(len(query_embedding), len(snippet_embedding))
        if min_len == 0:
            return 0.0
            
        query_vec = query_vec[:, :min_len]
        snippet_vec = snippet_vec[:, :min_len]
        
        # Calculate cosine similarity
        similarity = cosine_similarity(query_vec, snippet_vec)[0][0]
        return float(similarity)
    
    def search_snippets(self, query: str, snippets_with_embeddings: List[Tuple], limit: int = 10) -> List[Tuple]:
        """
        Search snippets using TF-IDF similarity
        """
        if not snippets_with_embeddings:
            return []
            
        # Extract all snippet texts for vectorization
        snippet_texts = []
        snippet_objects = []
        
        for snippet, embedding in snippets_with_embeddings:
            if snippet:
                # Combine snippet text
                combined_text = f"{snippet.title} {snippet.description or ''} {snippet.language} {snippet.code}"
                snippet_texts.append(combined_text)
                snippet_objects.append(snippet)
        
        if not snippet_texts:
            return []
        
        # Add query to the texts and vectorize everything together
        all_texts = snippet_texts + [query]
        
        try:
            # Fit and transform all texts
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Query vector is the last one
            query_vector = tfidf_matrix[-1]
            document_vectors = tfidf_matrix[:-1]
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, document_vectors).flatten()
            
            # Create results with similarity scores
            results = []
            for i, similarity in enumerate(similarities):
                if i < len(snippet_objects):
                    results.append((snippet_objects[i], float(similarity)))
            
            # Sort by similarity (highest first) and limit results
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:limit]
            
        except Exception as e:
            print(f"Search error: {e}")
            # Fallback: return all snippets with 0 similarity
            return [(snippet, 0.0) for snippet, _ in snippets_with_embeddings[:limit]]

# Global instance
search_service = SemanticSearchService()