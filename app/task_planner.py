from typing import List, Dict, Any
import re

class TaskPlanner:
    def __init__(self):
        self.task_patterns = {
            "email": {
                "compose": ["open gmail", "click compose", "enter recipient", "enter subject", "enter message", "send email"],
                "inbox": ["open gmail", "navigate to inbox", "check emails"],
                "search": ["open gmail", "use search box", "enter search terms", "review results"]
            },
            "web": {
                "search": ["open browser", "go to search engine", "enter search query", "click search", "review results"],
                "navigate": ["open browser", "enter url", "navigate to website", "interact with page"],
                "form": ["open browser", "navigate to form", "fill form fields", "submit form"]
            },
            "search": {
                "google": ["open browser", "go to google", "enter search query", "click search", "review results"],
                "information": ["open browser", "search for information", "analyze results", "extract relevant data"]
            }
        }
    
    def generate_task_steps(self, category: str, user_input: str, ui_context: Dict = None) -> List[str]:
        """
        Generate dynamic task steps based on category and user input
        """
        # Analyze user input for specific actions
        steps = self._analyze_user_intent(category, user_input)
        
        # Refine steps based on UI context if available
        if ui_context:
            steps = self._refine_with_context(steps, ui_context)
        
        return steps
    
    def _analyze_user_intent(self, category: str, user_input: str) -> List[str]:
        """
        Analyze user input to determine specific task type and generate steps
        """
        user_input_lower = user_input.lower()
        
        if category == "email":
            if any(word in user_input_lower for word in ["compose", "send", "write"]):
                return self._generate_compose_steps(user_input)
            elif any(word in user_input_lower for word in ["check", "inbox", "read"]):
                return self.task_patterns["email"]["inbox"]
            elif "search" in user_input_lower:
                return self.task_patterns["email"]["search"]
            else:
                return self.task_patterns["email"]["compose"]
        
        elif category == "web":
            if any(word in user_input_lower for word in ["search", "google", "find"]):
                return self._generate_search_steps(user_input)
            elif any(word in user_input_lower for word in ["goto", "visit", "navigate"]):
                return self._generate_navigation_steps(user_input)
            elif "form" in user_input_lower:
                return self.task_patterns["web"]["form"]
            else:
                return self._generate_search_steps(user_input)
        
        elif category == "search":
            return self._generate_search_steps(user_input)
        
        else:
            # Default web browsing steps
            return self.task_patterns["web"]["search"]
    
    def _generate_compose_steps(self, user_input: str) -> List[str]:
        """
        Generate email composition steps based on user input
        """
        steps = ["open gmail", "click compose button"]
        
        # Extract recipient if mentioned
        recipient_match = re.search(r'to\s+([^\s,]+@[^\s,]+)', user_input, re.IGNORECASE)
        if recipient_match:
            steps.append(f"enter recipient: {recipient_match.group(1)}")
        else:
            steps.append("enter recipient email")
        
        # Extract subject if mentioned
        subject_match = re.search(r'subject[:\s]+([^,.\n]+)', user_input, re.IGNORECASE)
        if subject_match:
            steps.append(f"enter subject: {subject_match.group(1).strip()}")
        else:
            steps.append("enter email subject")
        
        steps.extend(["enter email message", "click send button"])
        return steps
    
    def _generate_search_steps(self, user_input: str) -> List[str]:
        """
        Generate search steps based on user input
        """
        # Extract search query
        search_terms = self._extract_search_terms(user_input)
        
        steps = ["open browser", "navigate to google"]
        if search_terms:
            steps.append(f"search for: {search_terms}")
        else:
            steps.append("enter search query")
        
        steps.extend(["click search button", "review search results"])
        return steps
    
    def _generate_navigation_steps(self, user_input: str) -> List[str]:
        """
        Generate navigation steps based on user input
        """
        # Extract URL if mentioned
        url_match = re.search(r'https?://[^\s]+|www\.[^\s]+|[^\s]+\.(com|org|net|edu|gov)', user_input, re.IGNORECASE)
        
        steps = ["open browser"]
        if url_match:
            steps.append(f"go to: {url_match.group()}")
        else:
            steps.append("enter website url")
        
        steps.append("interact with webpage")
        return steps
    
    def _extract_search_terms(self, user_input: str) -> str:
        """
        Extract search terms from user input
        """
        # Remove common action words and extract core search terms
        stop_words = {'search', 'for', 'find', 'look', 'google', 'web', 'browse', 'about', 'information', 'on'}
        words = user_input.lower().split()
        search_words = [word for word in words if word not in stop_words and len(word) > 2]
        return ' '.join(search_words[:5])  # Limit to 5 words
    
    def _refine_with_context(self, steps: List[str], ui_context: Dict) -> List[str]:
        """
        Refine steps based on current UI context
        """
        # This method can be enhanced to adjust steps based on what's currently visible
        # For now, return steps as-is
        return steps