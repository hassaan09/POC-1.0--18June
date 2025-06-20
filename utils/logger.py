import logging
import os
from datetime import datetime
from config import Config

class Logger:
    def __init__(self):
        self.logger = logging.getLogger('gui_automation')
        if not self.logger.handlers:
            self.logger.setLevel(getattr(logging, Config.LOG_LEVEL))
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # File handler
            log_file = os.path.join(Config.DATA_DIR, 'automation.log')
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
    
    def log(self, message, level='INFO'):
        """Log message with specified level"""
        getattr(self.logger, level.lower())(message)
    
    def info(self, message):
        self.logger.info(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def warning(self, message):
        self.logger.warning(message)