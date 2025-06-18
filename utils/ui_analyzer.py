from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import json
from typing import Dict, List, Any

class UIAnalyzer:
    def __init__(self, browser_controller):
        self.browser = browser_controller
    
    def analyze_current_page(self) -> Dict[str, Any]:
        """
        Analyze current page and return UI tree structure
        """
        try:
            page_source = self.browser.get_page_source()
            url = self.browser.get_current_url()
            
            ui_tree = self._build_ui_tree(page_source)
            interactive_elements = self._find_interactive_elements()
            
            return {
                "url": url,
                "title": self.browser.driver.title,
                "ui_tree": ui_tree,
                "interactive_elements": interactive_elements,
                "page_type": self._detect_page_type(page_source, url)
            }
            
        except Exception as e:
            print(f"UI analysis failed: {e}")
            return {}
    
    def _build_ui_tree(self, html_source: str) -> Dict:
        """
        Build simplified UI tree from HTML source
        """
        soup = BeautifulSoup(html_source, 'html.parser')
        
        # Focus on interactive and important elements
        important_tags = ['input', 'button', 'a', 'form', 'select', 'textarea', 'div', 'span']
        
        ui_elements = []
        for tag in soup.find_all(important_tags):
            element_info = {
                "tag": tag.name,
                "id": tag.get('id', ''),
                "class": tag.get('class', []),
                "text": tag.get_text(strip=True)[:100],  # Limit text length
                "attributes": {k: v for k, v in tag.attrs.items() if k in ['name', 'type', 'href', 'role', 'aria-label']}
            }
            
            # Only include elements with meaningful content
            if element_info["id"] or element_info["text"] or element_info["attributes"]:
                ui_elements.append(element_info)
        
        return {"elements": ui_elements[:50]}  # Limit to first 50 elements
    
    def _find_interactive_elements(self) -> List[Dict]:
        """
        Find clickable and interactive elements on current page
        """
        interactive_elements = []
        
        try:
            # Find buttons
            buttons = self.browser.driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons[:10]:  # Limit to first 10
                try:
                    interactive_elements.append({
                        "type": "button",
                        "text": btn.text[:50],
                        "id": btn.get_attribute("id") or "",
                        "class": btn.get_attribute("class") or "",
                        "clickable": btn.is_enabled()
                    })
                except:
                    continue
            
            # Find links
            links = self.browser.driver.find_elements(By.TAG_NAME, "a")
            for link in links[:10]:  # Limit to first 10
                try:
                    interactive_elements.append({
                        "type": "link",
                        "text": link.text[:50],
                        "href": link.get_attribute("href") or "",
                        "id": link.get_attribute("id") or "",
                        "clickable": link.is_enabled()
                    })
                except:
                    continue
            
            # Find input fields
            inputs = self.browser.driver.find_elements(By.TAG_NAME, "input")
            for inp in inputs[:10]:  # Limit to first 10
                try:
                    interactive_elements.append({
                        "type": "input",
                        "input_type": inp.get_attribute("type") or "text",
                        "placeholder": inp.get_attribute("placeholder") or "",
                        "name": inp.get_attribute("name") or "",
                        "id": inp.get_attribute("id") or "",
                        "enabled": inp.is_enabled()
                    })
                except:
                    continue
                    
        except Exception as e:
            print(f"Interactive elements detection failed: {e}")
        
        return interactive_elements
    
    def _detect_page_type(self, html_source: str, url: str) -> str:
        """
        Detect the type of page for context-aware automation
        """
        url_lower = url.lower()
        html_lower = html_source.lower()
        
        if "gmail" in url_lower or "mail.google" in url_lower:
            return "gmail"
        elif "google" in url_lower and "search" in url_lower:
            return "google_search"
        elif "google" in url_lower:
            return "google_home"
        elif "login" in html_lower or "sign in" in html_lower:
            return "login_page"
        elif "form" in html_lower and ("submit" in html_lower or "send" in html_lower):
            return "form_page"
        else:
            return "generic_page"
    
    def find_element_by_text(self, text: str) -> Dict:
        """
        Find element containing specific text
        """
        try:
            elements = self.browser.driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
            if elements:
                element = elements[0]
                return {
                    "found": True,
                    "tag": element.tag_name,
                    "id": element.get_attribute("id") or "",
                    "class": element.get_attribute("class") or "",
                    "text": element.text
                }
        except:
            pass
        
        return {"found": False}
    
    def suggest_next_action(self, current_step: str, page_context: Dict) -> Dict:
        """
        Suggest next action based on current step and page context
        """
        page_type = page_context.get("page_type", "generic_page")
        step_lower = current_step.lower()
        
        suggestions = {
            "action": "unknown",
            "target": None,
            "method": "click"
        }
        
        if "click compose" in step_lower and page_type == "gmail":
            suggestions.update({
                "action": "click",
                "target": "compose",
                "method": "find_by_text",
                "search_terms": ["compose", "new message", "write"]
            })
        
        elif "search" in step_lower:
            suggestions.update({
                "action": "search",
                "target": "search_box",
                "method": "find_input",
                "search_terms": ["search", "q", "query"]
            })
        
        elif "enter" in step_lower or "type" in step_lower:
            suggestions.update({
                "action": "type",
                "target": "input_field",
                "method": "find_input"
            })
        
        elif "click" in step_lower:
            suggestions.update({
                "action": "click",
                "target": "button_or_link",
                "method": "find_clickable"
            })
        
        return suggestions