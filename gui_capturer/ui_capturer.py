import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
# Removed Service, ChromeDriverManager as they are now handled by main.py
from config import Config
from utils.logger import Logger
# Removed glob as it's now handled by main.py

class UICapturer:
    #  CHANGED: Constructor now accepts a driver instance
    def __init__(self, driver_instance):
        self.logger = Logger()
        self.driver = driver_instance #  ASSIGN: Use the provided driver instance
        self.logger.log(" UICapturer initialized with shared driver.")

    #  REMOVED: get_driver method, as the driver is now set externally
    # def get_driver(self):
    #    ... (this logic is now in main.py)


    def capture_state(self, step_number):
        """Capture screenshot and UI tree using the shared driver"""
        # Ensure driver is available (it should be, if correctly passed from main)
        if not self.driver:
            self.logger.log(" UICapturer: Driver not set. Cannot capture state.")
            return None, None

        # Take screenshot
        screenshot_path = os.path.join(
            Config.SCREENSHOTS_DIR,
            f"step{step_number}.png"
        )
        self.driver.save_screenshot(screenshot_path)
        self.logger.log(f" Screenshot saved to: {screenshot_path}")

        # Build UI tree
        ui_tree = self._build_ui_tree(self.driver)

        return screenshot_path, ui_tree

    def _build_ui_tree(self, driver):
        """Build minimal UI tree from DOM using the shared driver"""
        elements = []

        try:
            # Find interactive elements
            selectors = [
                "input", "button", "a", "select", "textarea",
                "[role='button']", "[role='link']", "[role='textbox']",
                "[tabindex]:not([tabindex='-1'])", #  ADDED: Elements with tabindex
                "div[onclick]", "span[onclick]" #  ADDED: Common clickable divs/spans
            ]

            for selector in selectors:
                web_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                #  IMPROVED: Filter for visible/enabled elements earlier
                visible_elements = [el for el in web_elements if el.is_displayed() and el.is_enabled()]
                for element in visible_elements[:Config.MAX_UI_ELEMENTS_TO_CAPTURE]: #  Use a config for limit
                    try:
                        rect = element.rect
                        # Basic filtering for tiny or off-screen elements that might be invisible
                        if rect['width'] > 0 and rect['height'] > 0 and rect['x'] >= 0 and rect['y'] >= 0:
                            element_data = {
                                "type": self._get_element_type(element),
                                "label": self._get_element_label(element),
                                "coordinates": [
                                    int(rect['x'] + rect['width'] / 2),
                                    int(rect['y'] + rect['height'] / 2)
                                ]
                            }
                            elements.append(element_data)
                    except Exception as inner_e:
                        self.logger.log(f" UICapturer: Error processing element for UI tree: {inner_e}")
                        continue

        except Exception as e:
            self.logger.log(f"Error building UI tree: {str(e)}")

        self.logger.log(f" Captured {len(elements)} interactive UI elements.")
        return {"elements": elements}

    def _get_element_type(self, element):
        """Determine element type"""
        tag_name = element.tag_name.lower()
        if tag_name == 'input':
            input_type = element.get_attribute('type') or 'text'
            return f"input_{input_type}"
        elif tag_name == 'a':
            return 'link'
        elif tag_name == 'img':
            return 'image'
        elif tag_name == 'select':
            return 'select'
        elif tag_name == 'textarea':
            return 'textarea'
        elif element.get_attribute('role'):
            return f"role_{element.get_attribute('role')}"
        return tag_name

    def _get_element_label(self, element):
        """Get element label or identifier"""
        # Try various attributes for label
        for attr in ['aria-label', 'placeholder', 'title', 'alt', 'name', 'value']: #  ADDED 'value'
            label = element.get_attribute(attr)
            if label and label.strip(): #  CHECK for non-empty string
                return label.strip()[:50]

        # Try text content
        text = element.text.strip()
        if text:
            return text[:50]

        # Fallback to tag and type
        return f"{element.tag_name}_{element.get_attribute('type') or 'unknown'}"