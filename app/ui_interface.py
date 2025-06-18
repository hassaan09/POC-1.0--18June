import os
from typing import Tuple, Optional
from PIL import Image

class UIInterface:
    def __init__(self, automation_agent):
        self.agent = automation_agent
    
    def process_task(self, text_input: Optional[str], 
                    audio_file: Optional[str], 
                    file_input: Optional[str]) -> Tuple[str, str, str, Optional[Image.Image]]:
        """
        Process task input and return results for Gradio interface
        """
        try:
            # Execute the task
            result = self.agent.process_task(text_input, audio_file, file_input)
            
            # Format status
            status = f"Status: {result['status'].title()}\nMessage: {result['message']}"
            
            # Format category
            category = result.get('category', 'Unknown')
            
            # Format steps
            steps = result.get('steps', 'No steps recorded')
            if result.get('original_input'):
                steps = f"Original Input: {result['original_input']}\n\n{steps}"
            
            # Load screenshot if available
            screenshot = None
            screenshot_path = result.get('screenshot')
            if screenshot_path and os.path.exists(screenshot_path):
                try:
                    screenshot = Image.open(screenshot_path)
                except Exception as e:
                    print(f"Failed to load screenshot: {e}")
            
            return status, category, steps, screenshot
            
        except Exception as e:
            error_status = f"Status: Error\nMessage: {str(e)}"
            return error_status, "Error", f"Failed to process task: {str(e)}", None
    
    def get_status_update(self) -> Tuple[str, str, str, Optional[Image.Image]]:
        """
        Get current status update
        """
        try:
            status_info = self.agent.get_current_status()
            
            status = f"Status: {status_info['status'].title()}\n"
            status += f"Browser Active: {status_info['browser_active']}\n"
            status += f"Current URL: {status_info['current_url']}\n"
            status += f"Steps Executed: {status_info['steps_executed']}"
            
            # Take current screenshot
            screenshot = None
            screenshot_path = self.agent.take_screenshot()
            if screenshot_path and os.path.exists(screenshot_path):
                try:
                    screenshot = Image.open(screenshot_path)
                except Exception as e:
                    print(f"Failed to load status screenshot: {e}")
            
            return status, "", "", screenshot
            
        except Exception as e:
            error_status = f"Status: Error\nMessage: Failed to get status: {str(e)}"
            return error_status, "", "", None
    
    def stop_automation(self) -> str:
        """
        Stop the automation
        """
        try:
            self.agent.stop_automation()
            return "Status: Stopped\nMessage: Automation stopped successfully"
        except Exception as e:
            return f"Status: Error\nMessage: Failed to stop automation: {str(e)}"