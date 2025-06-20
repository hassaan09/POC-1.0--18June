import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import Config
from utils.logger import Logger

class UICapturer:
    def __init__(self):
        self.logger = Logger()
        self.driver = None
        
    def get_driver(self):
        """Get current webdriver instance"""
        if not self.driver:
            chrome_options = webdriver.ChromeOptions()
            if Config.CHROME_HEADLESS:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(Config.IMPLICIT_WAIT)
            self.driver.maximize_window()
        return self.driver
        
    def capture_state(self, step_number):
        """Capture screenshot and UI tree"""
        driver = self.get_driver()
        
        # Take screenshot
        screenshot_path = os.path.join(
            Config.SCREENSHOTS_DIR, 
            f"step{step_number}.png"
        )
        driver.save_screenshot(screenshot_path)
        
        # Build UI tree
        ui_tree = self._build_ui_tree(driver)
        
        return screenshot_path, ui_tree
        
    def _build_ui_tree(self, driver):
        """Build minimal UI tree from DOM"""
        elements = []
        
        try:
            # Find interactive elements
            selectors = [
                "input", "button", "a", "select", "textarea",
                "[role='button']", "[role='link']", "[role='textbox']"
            ]
            
            for selector in selectors:
                web_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in web_elements[:10]:  # Limit to avoid token overflow
                    if element.is_displayed():
                        try:
                            rect = element.rect
                            element_data = {
                                "type": self._get_element_type(element),
                                "label": self._get_element_label(element),
                                "coordinates": [
                                    int(rect['x'] + rect['width']/2),
                                    int(rect['y'] + rect['height']/2)
                                ]
                            }
                            elements.append(element_data)
                        except:
                            continue
                            
        except Exception as e:
            self.logger.log(f"Error building UI tree: {str(e)}")
            
        return {"elements": elements}
        
    def _get_element_type(self, element):
        """Determine element type"""
        tag_name = element.tag_name.lower()
        if tag_name == 'input':
            input_type = element.get_attribute('type') or 'text'
            return f"input_{input_type}"
        return tag_name
        
    def _get_element_label(self, element):
        """Get element label or identifier"""
        # Try various attributes for label
        for attr in ['aria-label', 'placeholder', 'title', 'alt', 'name']:
            label = element.get_attribute(attr)
            if label:
                return label[:50]  # Truncate for token efficiency
                
        # Try text content
        text = element.text.strip()
        if text:
            return text[:50]
            
        # Fallback to tag and type
        return f"{element.tag_name}_{element.get_attribute('type') or 'unknown'}"