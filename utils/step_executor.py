import time
import re
from typing import Dict, List, Tuple, Any
from utils.ui_analyzer import UIAnalyzer

class StepExecutor:
    def __init__(self, browser_controller):
        self.browser = browser_controller
        self.ui_analyzer = UIAnalyzer(browser_controller)
        self.execution_log = []
    
    def execute_step(self, step: str, context: Dict = None) -> Tuple[bool, str, str]:
        """
        Execute a single automation step
        Returns: (success, message, screenshot_path)
        """
        step_lower = step.lower().strip()
        
        try:
            # Log the step
            self.execution_log.append(f"Executing: {step}")
            
            # Parse and execute based on step type
            if "open gmail" in step_lower:
                screenshot = self.browser.open_gmail()
                return True, "Gmail opened successfully", screenshot
            
            elif "open browser" in step_lower or "navigate to google" in step_lower:
                screenshot = self.browser.open_google()
                return True, "Browser opened with Google", screenshot
            
            elif "go to" in step_lower:
                url = self._extract_url_from_step(step)
                screenshot = self.browser.open_url(url)
                return True, f"Navigated to {url}", screenshot
            
            elif "click compose" in step_lower:
                success = self._click_compose_button()
                screenshot = self.browser.take_screenshot("compose_clicked")
                return success, "Compose button clicked" if success else "Failed to click compose", screenshot
            
            elif "search for" in step_lower or "enter search" in step_lower:
                query = self._extract_search_query(step)
                screenshot = self.browser.search_google(query)
                return True, f"Searched for: {query}", screenshot
            
            elif "enter recipient" in step_lower:
                recipient = self._extract_recipient(step)
                success = self._enter_email_recipient(recipient)
                screenshot = self.browser.take_screenshot("recipient_entered")
                return success, f"Recipient entered: {recipient}" if success else "Failed to enter recipient", screenshot
            
            elif "enter subject" in step_lower:
                subject = self._extract_subject(step)
                success = self._enter_email_subject(subject)
                screenshot = self.browser.take_screenshot("subject_entered")
                return success, f"Subject entered: {subject}" if success else "Failed to enter subject", screenshot
            
            elif "enter message" in step_lower or "enter email message" in step_lower:
                success = self._enter_email_message()
                screenshot = self.browser.take_screenshot("message_entered")
                return success, "Email message entered" if success else "Failed to enter message", screenshot
            
            elif "send" in step_lower and "email" in step_lower:
                success = self._send_email()
                screenshot = self.browser.take_screenshot("email_sent")
                return success, "Email sent successfully" if success else "Failed to send email", screenshot
            
            elif "click" in step_lower:
                target = self._extract_click_target(step)
                success = self._generic_click(target)
                screenshot = self.browser.take_screenshot("clicked")
                return success, f"Clicked: {target}" if success else f"Failed to click: {target}", screenshot
            
            else:
                # Generic step handling
                success = self._handle_generic_step(step)
                screenshot = self.browser.take_screenshot("generic_step")
                return success, f"Executed generic step: {step}" if success else f"Failed to execute: {step}", screenshot
        
        except Exception as e:
            screenshot = self.browser.take_screenshot("error")
            return False, f"Error executing step: {str(e)}", screenshot
    
    def _click_compose_button(self) -> bool:
        """
        Click Gmail compose button using multiple strategies
        """
        strategies = [
            ("xpath", "//div[@role='button'][contains(.,'Compose')]"),
            ("xpath", "//*[contains(text(), 'Compose')]"),
            ("xpath", "//div[contains(@class, 'compose')]"),
            ("xpath", "//button[contains(text(), 'Compose')]")
        ]
        
        for strategy_type, selector in strategies:
            if strategy_type == "xpath":
                if self.browser.find_and_click(element_xpath=selector):
                    return True
        
        return False
    
    def _enter_email_recipient(self, recipient: str) -> bool:
        """
        Enter email recipient in Gmail compose
        """
        strategies = [
            ("name", "to"),
            ("xpath", "//input[@name='to']"),
            ("xpath", "//textarea[contains(@aria-label, 'To')]"),
            ("xpath", "//*[@role='combobox']")
        ]
        
        for strategy_type, selector in strategies:
            if strategy_type == "name":
                if self.browser.find_and_type(recipient, element_name=selector):
                    return True
            elif strategy_type == "xpath":
                if self.browser.find_and_type(recipient, element_xpath=selector):
                    return True
        
        return False
    
    def _enter_email_subject(self, subject: str) -> bool:
        """
        Enter email subject in Gmail compose
        """
        strategies = [
            ("name", "subjectbox"),
            ("xpath", "//input[@name='subjectbox']"),
            ("xpath", "//input[contains(@aria-label, 'Subject')]")
        ]
        
        for strategy_type, selector in strategies:
            if strategy_type == "name":
                if self.browser.find_and_type(subject, element_name=selector):
                    return True
            elif strategy_type == "xpath":
                if self.browser.find_and_type(subject, element_xpath=selector):
                    return True
        
        return False
    
    def _enter_email_message(self) -> bool:
        """
        Enter email message body - prompt user for manual input
        """
        print("Please enter your email message manually in the compose window...")
        return self.browser.wait_for_manual_input(timeout=30)
    
    def _send_email(self) -> bool:
        """
        Click send button in Gmail
        """
        strategies = [
            ("xpath", "//div[@role='button'][contains(.,'Send')]"),
            ("xpath", "//*[contains(text(), 'Send')]"),
            ("xpath", "//button[contains(text(), 'Send')]")
        ]
        
        for strategy_type, selector in strategies:
            if strategy_type == "xpath":
                if self.browser.find_and_click(element_xpath=selector):
                    return True
        
        return False
    
    def _generic_click(self, target: str) -> bool:
        """
        Generic click handler for any text-based target
        """
        return self.browser.find_and_click(element_text=target)
    
    def _handle_generic_step(self, step: str) -> bool:
        """
        Handle generic steps by analyzing current page context
        """
        page_context = self.ui_analyzer.analyze_current_page()
        suggestion = self.ui_analyzer.suggest_next_action(step, page_context)
        
        if suggestion["action"] == "click":
            return self._generic_click(suggestion.get("target", ""))
        elif suggestion["action"] == "search":
            query = self._extract_search_query(step)
            return bool(self.browser.search_google(query))
        
        return True  # Default to success for unknown steps
    
    def _extract_url_from_step(self, step: str) -> str:
        """
        Extract URL from step text
        """
        url_match = re.search(r'https?://[^\s]+|www\.[^\s]+|[^\s]+\.(com|org|net|edu|gov)', step, re.IGNORECASE)
        if url_match:
            return url_match.group()
        
        # Extract after "go to" or "visit"
        match = re.search(r'(?:go to|visit)\s+([^\s]+)', step, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return "google.com"
    
    def _extract_search_query(self, step: str) -> str:
        """
        Extract search query from step text
        """
        # Look for "search for: query" pattern
        match = re.search(r'search for[:\s]+(.+)', step, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Extract text after search-related keywords
        patterns = [
            r'search\s+(.+)',
            r'find\s+(.+)',
            r'look for\s+(.+)',
            r'query[:\s]+(.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, step, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "search query"
    
    def _extract_recipient(self, step: str) -> str:
        """
        Extract recipient email from step text
        """
        # Look for email pattern
        email_match = re.search(r'[^\s]+@[^\s]+', step)
        if email_match:
            return email_match.group()
        
        # Look for "recipient: email" pattern
        match = re.search(r'recipient[:\s]+([^\s,]+)', step, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return "recipient@example.com"
    
    def _extract_subject(self, step: str) -> str:
        """
        Extract email subject from step text
        """
        # Look for "subject: text" pattern
        match = re.search(r'subject[:\s]+(.+)', step, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return "Email Subject"
    
    def _extract_click_target(self, step: str) -> str:
        """
        Extract click target from step text
        """
        # Remove "click" and common words
        cleaned = re.sub(r'\b(click|button|link|on|the)\b', '', step, flags=re.IGNORECASE)
        return cleaned.strip()
    
    def get_execution_log(self) -> List[str]:
        """
        Get execution log
        """
        return self.execution_log.copy()
    
    def clear_log(self):
        """
        Clear execution log
        """
        self.execution_log.clear()