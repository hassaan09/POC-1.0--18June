import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from config import Config
from utils.logger import Logger

class TaskRetriever:
    def __init__(self):
        self.logger = Logger()
        self.dataset = []
        self.vectorizer = None
        self.task_vectors = None
        self._load_dataset()
        self._build_index()
        
    def _load_dataset(self):
        """Load GUI automation dataset"""
        try:
            if os.path.exists(Config.DATASET_PATH):
                with open(Config.DATASET_PATH, 'r') as f:
                    self.dataset = json.load(f)
            else:
                # Create sample dataset if not exists
                self._create_sample_dataset()
                
        except Exception as e:
            self.logger.log(f"Error loading dataset: {str(e)}")
            self._create_sample_dataset()
            
    def _create_sample_dataset(self):
        """Create sample dataset for POC"""
        sample_data = [
            {
                "query": "Navigate to Facebook login page",
                "steps": [
                    {
                        "ui_tree": {
                            "elements": [
                                {
                                    "type": "input_text",
                                    "label": "Search Box",
                                    "coordinates": [165, 324]
                                }
                            ]
                        },
                        "action": {
                            "type": "click",
                            "element": "Search Box",
                            "coordinates": [145, 101]
                        }
                    },
                    {
                        "ui_tree": {
                            "elements": [
                                {
                                    "type": "input_text",
                                    "label": "Search Box",
                                    "coordinates": [288, 233]
                                }
                            ]
                        },
                        "action": {
                            "type": "type",
                            "element": "Search Box",
                            "text": "facebook.com"
                        }
                    }
                ]
            },
            {
                "query": "Search for weather information",
                "steps": [
                    {
                        "ui_tree": {
                            "elements": [
                                {
                                    "type": "input_text",
                                    "label": "Search",
                                    "coordinates": [400, 200]
                                }
                            ]
                        },
                        "action": {
                            "type": "click",
                            "element": "Search",
                            "coordinates": [400, 200]
                        }
                    }
                ]
            }
        ]
        
        self.dataset = sample_data
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        with open(Config.DATASET_PATH, 'w') as f:
            json.dump(sample_data, f, indent=2)
            
    def _build_index(self):
        """Build TF-IDF index for retrieval"""
        if not self.dataset:
            return
            
        queries = [item['query'] for item in self.dataset]
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.task_vectors = self.vectorizer.fit_transform(queries)
        
    def retrieve_similar(self, query, top_k=None):
        """Retrieve similar tasks using TF-IDF"""
        if not self.vectorizer or not self.task_vectors.shape[0]:
            return []
            
        if top_k is None:
            top_k = Config.TOP_K_RESULTS
            
        try:
            query_vector = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vector, self.task_vectors).flatten()
            
            # Get top-k most similar
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum similarity threshold
                    results.append({
                        'query': self.dataset[idx]['query'],
                        'steps': self.dataset[idx]['steps'],
                        'similarity': float(similarities[idx])
                    })
                    
            return results
            
        except Exception as e:
            self.logger.log(f"Error in retrieval: {str(e)}")
            return []