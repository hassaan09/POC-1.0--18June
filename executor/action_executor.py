import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Removed Service, ChromeDriverManager, Options as they are now handled by main.py
from config import Config
from utils.logger import Logger
from selenium.webdriver.common.action_chains import ActionChains
import os
import glob


class ActionExecutor:
    # CHANGED: Constructor now accepts a driver instance
    def __init__(self, driver_instance):
        self.logger = Logger()
        self.driver = driver_instance # ASSIGN: Use the provided driver instance
        self.wait = WebDriverWait(self.driver, Config.EXPLICIT_WAIT) # INITIALIZE: Wait object here
        self.actions = ActionChains(self.driver) # INITIALIZE: ActionChains here
        self.logger.log("ActionExecutor initialized with shared driver.")


    # REMOVED: initialize_browser method, as browser is now initialized externally
    # def initialize_browser(self):
    #    ... (this logic is now in main.py)


    def execute_action(self, action_suggestion):
        """Execute suggested action"""
        # No need for an internal driver check/init, driver is guaranteed to be set
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
            elif action_type == 'finish':
                self.logger.log("Task completed successfully.")
                return True
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
            self.logger.log(f"Attempting to click: {target_element} at coordinates {element.location['x']},{element.location['y']}")
            self.driver.execute_script("arguments[0].style.border='3px solid lime; background-color: yellow;'", element) # custom added 25 June
            try:
                # Try using ActionChains for better reliability
                self.actions.move_to_element(element).click().perform()
                self.logger.log(f"Clicked: {target_element}")
            except Exception as click_error:
                self.logger.log(f"Failed direct click for {target_element}: {click_error}. Trying JS click.")
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                    self.logger.log(f"Clicked (JS): {target_element}")
                except Exception as js_click_error:
                    self.logger.log(f"Failed JS click for {target_element}: {js_click_error}")
                    return False

            #  Post-click: Wait for Google search result page (if applicable)
            try:
                self.logger.log("Waiting for search result container to load...")
                self.wait.until(EC.presence_of_element_located((By.ID, "search")))
                self.logger.log(" Search results page detected.")
            except Exception as wait_error:
                self.logger.log(f" Search results container not detected: {wait_error}")

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

    # def _find_element(self, target_description):
        """Find element by various strategies"""
        if not target_description or not target_description.strip():
            self.logger.log("Empty or invalid target description — skipping element search.")
            return None

        # ADDED: Lowercase target_description for case-insensitive matching in some strategies
        target_description = target_description.strip() # Added custom 26 June
        target_description_lower = target_description.lower()

        strategies = [
            # By exact placeholder (case-insensitive for safety, though exact is often needed)
            (By.CSS_SELECTOR, f"input[placeholder='{target_description}']"),
            (By.CSS_SELECTOR, f"input[placeholder*='{target_description}']"), # Contains

            # By exact aria-label
            (By.CSS_SELECTOR, f"[aria-label='{target_description}']"),
            (By.CSS_SELECTOR, f"[aria-label*='{target_description}']"), # Contains

            # By text content (case-insensitive for robustness)
            (By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_description_lower}')]"),
            (By.XPATH, f"//*[normalize-space(.)='{target_description}']"), # Exact visible text

            # By name attribute
            (By.NAME, target_description),
            # By id
            (By.ID, target_description),
            # Common search box patterns (these are often generic)
            (By.CSS_SELECTOR, "input[type='search']"),
            (By.CSS_SELECTOR, "input[name='q']"),
            (By.CSS_SELECTOR, "input[name='search']"),
            # By title attribute
            (By.CSS_SELECTOR, f"[title*='{target_description}']"),
            # By value attribute (for inputs)
            (By.CSS_SELECTOR, f"input[value*='{target_description}']"),
        ]

        for strategy in strategies:
            try:
                # Use self.wait for finding elements to ensure they are present/visible
                element = self.wait.until(EC.presence_of_element_located(strategy))
                if element.is_displayed() and element.is_enabled():
                    self.logger.log(f"Found element by strategy {strategy}: {element.tag_name} - {self._get_element_label_for_logging(element)}")
                    return element
            except Exception as e:
                # self.logger.log(f"ActionExecutor: No element found with strategy {strategy}: {e}") # Too verbose
                continue

        self.logger.log(f"ActionExecutor: No element found for target: {target_description}")
        return None

    
        """Find element by various strategies"""
        if not target_description or not target_description.strip():
            self.logger.log(" Empty or invalid target description — skipping element search.")
            return None

        target_description = target_description.strip()
        target_description_lower = target_description.lower()

        strategies = [
            # By exact placeholder
            (By.CSS_SELECTOR, f"input[placeholder='{target_description}']"),
            (By.CSS_SELECTOR, f"input[placeholder*='{target_description}']"),

            # By aria-label
            (By.CSS_SELECTOR, f"[aria-label='{target_description}']"),
            (By.CSS_SELECTOR, f"[aria-label*='{target_description}']"),

            # By visible text (case-insensitive, normalized)
            (By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_description_lower}')]"),
            (By.XPATH, f"//*[normalize-space(.)='{target_description}']"),

            # By name, id, title, value
            (By.NAME, target_description),
            (By.ID, target_description),
            (By.CSS_SELECTOR, f"[title*='{target_description}']"),
            (By.CSS_SELECTOR, f"input[value*='{target_description}']"),

            # Common input patterns
            (By.CSS_SELECTOR, "input[type='search']"),
            (By.CSS_SELECTOR, "input[name='q']"),
            (By.CSS_SELECTOR, "input[name='search']"),

            #  Final fallback: <a> link text match (like 'Sign into Gmail')
            (By.XPATH, f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_description_lower}')]")
        ]

        for strategy in strategies:
            try:
                element = self.wait.until(EC.presence_of_element_located(strategy))
                if element.is_displayed() and element.is_enabled():
                    self.logger.log(f" Found element by strategy {strategy}: {element.tag_name} - {self._get_element_label_for_logging(element)}")
                    return element
            except Exception:
                continue

        self.logger.log(f" No element found for target: '{target_description}'")
        return None

    # Custom added 26 June
    def _find_element(self, target_description):
        """Find element by various strategies"""
        if not target_description or not target_description.strip():
            self.logger.log(" Empty or invalid target description — skipping element search.")
            return None

        target_description = target_description.strip()
        target_description_lower = target_description.lower()

        strategies = [
            (By.CSS_SELECTOR, f"input[placeholder='{target_description}']"),
            (By.CSS_SELECTOR, f"input[placeholder*='{target_description}']"),
            (By.CSS_SELECTOR, f"[aria-label='{target_description}']"),
            (By.CSS_SELECTOR, f"[aria-label*='{target_description}']"),
            (By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_description_lower}')]"),
            (By.XPATH, f"//*[normalize-space(.)='{target_description}']"),
            (By.NAME, target_description),
            (By.ID, target_description),
            (By.CSS_SELECTOR, "input[type='search']"),
            (By.CSS_SELECTOR, "input[name='q']"),
            (By.CSS_SELECTOR, "input[name='search']"),
            (By.CSS_SELECTOR, f"[title*='{target_description}']"),
            (By.CSS_SELECTOR, f"input[value*='{target_description}']"),

            #  FINAL fallback for links (anchors) with partial text match
            (By.XPATH, f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_description_lower}')]"),
            (By.XPATH, f"//a[normalize-space(text())='{target_description}']")
        ]

        for strategy in strategies:
            try:
                # self.logger.log(f" Trying strategy {strategy} for target '{target_description}'")
                element = self.wait.until(EC.presence_of_element_located(strategy))
                if element.is_displayed() and element.is_enabled():
                    self.logger.log(f" Found element by {strategy}: {self._get_element_label_for_logging(element)}")
                    return element
            except Exception as e:
                self.logger.log(f" Strategy {strategy} failed: {e}")
                continue
        # 26 June custom added  - Brute force
        try:
            anchors = self.driver.find_elements(By.TAG_NAME, "a")
            for anchor in anchors:
                visible_text = anchor.text.strip().lower()
                if visible_text == target_description.lower():
                    self.logger.log(f" Matched via brute-force <a> tag text: '{visible_text}' == '{target_description}'")
                    self.driver.execute_script("arguments[0].style.border='3px solid red'", anchor)
                    return anchor

        except Exception as e:
            self.logger.log(f" Fallback <a> tag match failed: {e}")
        
        try:
            links = self.driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                text = link.text.strip()
                if text:
                    self.logger.log(f"[A]  Found link text: '{text}'")
        except Exception as e:
                    self.logger.log(f"Error while listing <a> tags: {e}")

        self.logger.log(f" No element found for target: '{target_description}'")
        
        return None


    def _get_element_label_for_logging(self, element):
        """Helper to get a log-friendly label for found elements"""
        # Prioritize easily identifiable attributes for logging
        for attr in ['id', 'name', 'aria-label', 'placeholder', 'title', 'value']:
            value = element.get_attribute(attr)
            if value:
                return f"{attr}='{value[:50]}'" # Truncate for logging
        if element.text:
            return f"text='{element.text[:50]}'"
        return f"tag='{element.tag_name}'"

    # REMOVED: cleanup method, as the shared driver is cleaned up by main.py
    # def cleanup(self):
    #    ...
