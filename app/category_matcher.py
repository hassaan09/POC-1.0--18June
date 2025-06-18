from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import Dict, Tuple
from app.config import Config

class CategoryMatcher:
    def __init__(self):
        self.categories = Config.CATEGORIES
        self.vectorizer = TfidfVectorizer(
            max_features=Config.MAX_FEATURES,
            min_df=Config.MIN_DF,
            stop_words='english',
            lowercase=True
        )
        self._prepare_category_vectors()
    
    def _prepare_category_vectors(self):
        """
        Prepare TF-IDF vectors for all categories
        """
        category_texts = []
        self.category_ids = []
        
        for category_id, category_data in self.categories.items():
            # Combine name, description, and keywords
            text = f"{category_data['name']} {category_data['description']} {' '.join(category_data['keywords'])}"
            category_texts.append(text)
            self.category_ids.append(category_id)
        
        self.category_vectors = self.vectorizer.fit_transform(category_texts)
    
    def match_category(self, user_input: str, threshold: float = 0.1) -> Tuple[str, float]:
        """
        Match user input to the most relevant category using TF-IDF similarity
        """
        if not user_input.strip():
            return "web", 0.0
        
        # Transform user input to vector
        input_vector = self.vectorizer.transform([user_input.lower()])
        
        # Calculate cosine similarity with all categories
        similarities = cosine_similarity(input_vector, self.category_vectors).flatten()
        
        # Find best match
        best_idx = np.argmax(similarities)
        best_score = similarities[best_idx]
        best_category = self.category_ids[best_idx]
        
        # Apply threshold for confidence
        if best_score < threshold:
            return "web", best_score  # Default to web if no good match
        
        return best_category, best_score
    
    def get_category_info(self, category_id: str) -> Dict:
        """
        Get category information
        """
        return self.categories.get(category_id, self.categories["web"])
    
    def get_initial_action(self, category_id: str) -> str:
        """
        Get the initial action for a category
        """
        category_info = self.get_category_info(category_id)
        return category_info.get("initial_action", "open_browser")