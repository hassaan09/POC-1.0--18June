import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Config:
    # Browser settings
    IMPLICIT_WAIT = 10
    EXPLICIT_WAIT = 30
    SCREENSHOT_DIR = "screenshots"
    
    # Audio settings
    AUDIO_SAMPLE_RATE = 16000
    AUDIO_CHANNELS = 1
    
    # TF-IDF settings
    MAX_FEATURES = 1000
    MIN_DF = 1
    
    # Categories configuration
    CATEGORIES = {
        "email": {
            "name": "Email Operations",
            "description": "Compose, send, manage emails",
            "keywords": ["email", "gmail", "compose", "send", "inbox", "mail", "message"],
            "initial_action": "open_gmail"
        },
        "web": {
            "name": "Web Browsing",
            "description": "Navigate, interact with websites",
            "keywords": ["web", "browse", "website", "navigate", "search", "google", "url"],
            "initial_action": "open_browser"
        },
        "file": {
            "name": "File Operations",
            "description": "Create, edit, delete files",
            "keywords": ["file", "document", "create", "edit", "delete", "folder", "save"],
            "initial_action": "open_file_manager"
        },
        "app": {
            "name": "Application Control",
            "description": "Launch/control applications",
            "keywords": ["app", "application", "launch", "open", "program", "software"],
            "initial_action": "launch_app"
        },
        "search": {
            "name": "Search Operations",
            "description": "Retrieve info via search",
            "keywords": ["search", "find", "look", "query", "information", "data"],
            "initial_action": "perform_search"
        }
    }
    
    # Chrome options
    CHROME_OPTIONS = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled",
        "--disable-extensions",
        "--disable-plugins",
        "--disable-images",
        "--disable-javascript"
    ]