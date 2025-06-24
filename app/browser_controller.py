from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from app.config import Config
import glob
import utils.logger as Logger

class BrowserController:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.actions = None
        self._setup_driver()
    
    def _setup_driver(self):
        """
        Initialize Chrome driver with optimal settings
        """
        print("[INFO] BrowserController: Driver initialized with waits - Implicit:", Config.IMPLICIT_WAIT, ", Explicit:", Config.EXPLICIT_WAIT)


        if self.driver: 
            self.logger.log(" BrowserController: Driver already initialized.", level='debug')
            return

        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Create screenshots directory
        os.makedirs(Config.SCREENSHOT_DIR, exist_ok=True)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(Config.IMPLICIT_WAIT)
        self.driver.maximize_window()
        
        # Remove automation indicators
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.wait = WebDriverWait(self.driver, Config.EXPLICIT_WAIT)
        self.actions = ActionChains(self.driver)
    
    def open_gmail(self):
        """
        Open Gmail in browser
        """
        self.driver.get("https://gmail.com")
        return self.take_screenshot("gmail_opened")
    
    def open_google(self):
        """
        Open Google search
        """
        self.driver.get("https://google.com")
        return self.take_screenshot("google_opened")
    
    def open_url(self, url: str):
        """
        Navigate to specific URL
        """
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        self.driver.get(url)
        return self.take_screenshot("url_opened")
    
    def find_and_click(self, element_text: str = None, element_id: str = None, 
                      element_class: str = None, element_xpath: str = None):
        """
        Find and click element using various selectors
        """
        try:
            element = None
            
            if element_xpath:
                print(f"[DEBUG] Trying to click element with XPATH: {element_xpath}")
                element = self.wait.until(EC.element_to_be_clickable((By.XPATH, element_xpath)))
            elif element_id:
                print(f"[DEBUG] Trying to click element with ID: {element_id}")
                element = self.wait.until(EC.element_to_be_clickable((By.ID, element_id)))
            elif element_class:
                print(f"[DEBUG] Trying to click element with CLASS: {element_class}")
                element = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, element_class)))
            elif element_text:
                # Try to find by text content
                print(f"[DEBUG] Trying to click element with TEXT: {element_text}")
                xpath = f"//*[contains(text(), '{element_text}')]"
                element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            
            if element:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)
                element.click()
                return True
                
        except Exception as e:
            print(f"Click failed: {e}")
            return False
    
    def find_and_type(self, text: str, element_id: str = None, 
                     element_class: str = None, element_xpath: str = None,
                     element_name: str = None):
        """
        Find input field and type text
        """
        try:
            element = None
            
            if element_xpath:
                print(f"[DEBUG] Trying to type in element with XPATH: {element_xpath}")
                element = self.wait.until(EC.presence_of_element_located((By.XPATH, element_xpath)))
            elif element_id:
                print(f"[DEBUG] Trying to type in element with ID: {element_id}")
                element = self.wait.until(EC.presence_of_element_located((By.ID, element_id)))
            elif element_class:
                print(f"[DEBUG] Trying to type in element with CLASS: {element_class}")
                element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, element_class)))
            elif element_name:
                print(f"[DEBUG] Trying to type in element with NAME: {element_name}")
                element = self.wait.until(EC.presence_of_element_located((By.NAME, element_name)))
            
            if element:
                element.clear()
                element.send_keys(text)
                return True
                
        except Exception as e:
            print(f"Type failed: {e}")
            return False
    
    def search_google(self, query: str):
        """
        Perform Google search
        """
        try:
            # Find search box
            search_box = self.wait.until(EC.presence_of_element_located((By.NAME, "q")))
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            
            # Wait for results
            self.wait.until(EC.presence_of_element_located((By.ID, "search")))
            return self.take_screenshot("search_results")
            
        except Exception as e:
            print(f"Search failed: {e}")
            return None
    
    def wait_for_manual_input(self, timeout: int = 60, success_indicator: str = None):
        """
        Wait for user to manually complete an action (like login)
        """
        print(f"Please complete the manual input within {timeout} seconds...")
        
        if success_indicator:
            try:
                self.wait.until(EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{success_indicator}')]")))
                print("Manual input completed. Resuming automation...")
                return True
            except:
                print("Manual input timeout or failed.")
                return False
        else:
            time.sleep(timeout)
            return True
    
    def take_screenshot(self, name: str = None) -> str:
        """
        Take screenshot and return file path
        """
        if not name:
            name = f"screenshot_{int(time.time())}"
        
        screenshot_path = os.path.join(Config.SCREENSHOT_DIR, f"{name}.png")
        self.driver.save_screenshot(screenshot_path)
        return screenshot_path
    
    def get_page_source(self) -> str:
        """
        Get current page HTML source
        """
        return self.driver.page_source
    
    def get_current_url(self) -> str:
        """
        Get current page URL
        """
        return self.driver.current_url
    
    def close(self):
        """
        Close browser
        """
        if self.driver:
            self.driver.quit()