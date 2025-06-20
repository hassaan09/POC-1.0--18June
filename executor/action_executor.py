import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import Config
from utils.logger import Logger

class ActionExecutor:
    def __init__(self):
        self.logger = Logger()
        self.driver = None
        self.wait = None
        
    def initialize_browser(self):
        """Initialize Chrome browser"""
        if self.driver:
            return
            
        chrome_options = webdriver.ChromeOptions()
        if Config.CHROME_HEADLESS:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(Config.IMPLICIT_WAIT)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, Config.EXPLICIT_WAIT)
        
        # Start with Google homepage
        self.driver.get("https://www.google.com")
        
    def execute_action(self, action_suggestion):
        """Execute suggested action"""
        if not self.driver:
            self.initialize_browser()
            
        action_type = action_suggestion.get('action_type', 'wait')
        target_element = action_suggestion.get('target_element', '')
        additional_input = action_suggestion.get('additional_input', '')
        
        try:
            if action_type == 'click':
                return self._execute_click(target_element)
            elif action_type == 'type':
                return self._execute_type(target_element, additional_input)
            elif action_type == 'navigate':
                return self._execute_navigate(additional_input)
            elif action_type == 'wait':
                return self._execute_wait()
            else:
                self.logger.log(f"Unknown action type: {action_type}")
                return False
                
        except Exception as e:
            self.logger.log(f"Error executing action: {str(e)}")
            return False
            
    def _execute_click(self, target_element):
        """Execute click action"""
        element = self._find_element(target_element)
        if element:
            element.click()
            self.logger.log(f"Clicked: {target_element}")
            return True
        return False
        
    def _execute_type(self, target_element, text):
        """Execute type action"""
        element = self._find_element(target_element)
        if element:
            element.clear()
            element.send_keys(text)
            self.logger.log(f"Typed '{text}' in: {target_element}")
            return True
        return False
        
    def _execute_navigate(self, url):
        """Execute navigate action"""
        if not url.startswith('http'):
            url = 'https://' + url
        self.driver.get(url)
        self.logger.log(f"Navigated to: {url}")
        return True
        
    def _execute_wait(self):
        """Execute wait action"""
        self.logger.log("Manual intervention required")
        return True
        
    def _find_element(self, target_description):
        """Find element by various strategies"""
        if not target_description:
            return None
            
        strategies = [
            # By placeholder
            (By.CSS_SELECTOR, f"input[placeholder*='{target_description}']"),
            # By aria-label
            (By.CSS_SELECTOR, f"[aria-label*='{target_description}']"),
            # By text content
            (By.XPATH, f"//*[contains(text(), '{target_description}')]"),
            # By name attribute
            (By.NAME, target_description),
            # By id
            (By.ID, target_description),
            # Common search box patterns
            (By.CSS_SELECTOR, "input[type='search']"),
            (By.CSS_SELECTOR, "input[name='q']"),
            (By.CSS_SELECTOR, "input[name='search']"),
        ]
        
        for strategy in strategies:
            try:
                elements = self.driver.find_elements(*strategy)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        return element
            except:
                continue
                
        return None
        
    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()
            self.driver = None