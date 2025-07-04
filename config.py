import os

class Config:
    # ADDITIONAL CONFIGURATION
    ACTION_DELAY = 2 # Seconds to pause between actions for visual observation
    MAX_UI_ELEMENTS_TO_CAPTURE = 20 # Limit the number of elements in UI tree for LLM context
    MAX_AUTOMATION_STEPS = 10  # Maximum steps to prevent infinite loops  

    # API Configuration
    OPENAI_API_KEY = ''
    OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'
    
    # Selenium Configuration
    IMPLICIT_WAIT = 2
    EXPLICIT_WAIT = 2
    CHROME_HEADLESS = False
    
    # Retrieval Configuration
    TOP_K_RESULTS = 3
    
    # File Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    SCREENSHOTS_DIR = os.path.join(DATA_DIR, 'screenshots')
    DATASET_PATH = os.path.join(DATA_DIR, 'gui_demos.json')
    
    # UI Configuration
    GRADIO_PORT = 7860
    GRADIO_SHARE = False
    
    # Logging
    LOG_LEVEL = 'INFO'
    
    @classmethod
    def create_directories(cls):
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.SCREENSHOTS_DIR, exist_ok=True)