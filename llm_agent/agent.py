import json
import requests
from config import Config
from llm_agent.prompt_templates import PromptTemplates
from utils.logger import Logger
import traceback

class LLMAgent:
    def __init__(self):
        self.logger = Logger()
        self.prompt_templates = PromptTemplates()
        
    def get_action_suggestion(self, instruction, ui_tree, retrieved_examples, screenshot_path):
        """Get action suggestion from LLM"""
        try:
            prompt = self.prompt_templates.build_action_prompt(
                instruction, ui_tree, retrieved_examples, screenshot_path
            )
            
            response = self._call_openai_api(prompt)
            action_suggestion = self._parse_response(response)
            
            return action_suggestion
            
        except Exception as e:
            # tb = traceback.format_exc()
            # self.logger.log(f"Error getting LLM suggestion: {str(e)}\nTraceback: {tb}")
            self.logger.log(f"Error getting LLM suggestion: {str(e)}")
            return {"action_type": "wait", "target_element": "unknown"}
            
    def _call_openai_api(self, prompt):
        """Call OpenAI API"""
        headers = {
            'Authorization': f'Bearer {Config.OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {
                    'role': 'system',
                    'content': self.prompt_templates.get_system_prompt()
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 200,
            'temperature': 0.1
        }
        
       
        response = requests.post(Config.OPENAI_API_URL, headers=headers, json=data)
        try:
            # self.logger.log(f"LLM API raw response: {response.text}")
            result = response.json()
        except Exception as e:
            self.logger.log(f"Error decoding LLM response JSON: {str(e)}")
            raise
        response.raise_for_status()
        
        return response.json()['choices'][0]['message']['content']
        
    def _parse_response(self, response):
        """Parse LLM response to action format"""
        try:
            # Try to parse JSON response
            if '{' in response and '}' in response:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                json_str = response[json_start:json_end]
                action = json.loads(json_str)
                
                # Validate required fields
                if 'action_type' not in action:
                    action['action_type'] = 'wait'
                if 'target_element' not in action:
                    action['target_element'] = 'unknown'
                    
                return action
            else:
                # Fallback parsing
                return self._fallback_parse(response)
                
        except Exception as e:
            self.logger.log(f"Error parsing response: {str(e)}")
            return {"action_type": "wait", "target_element": "unknown"}
            
    def _fallback_parse(self, response):
        """Fallback response parsing"""
        response_lower = response.lower()
        
        if 'click' in response_lower:
            return {"action_type": "click", "target_element": "button"}
        elif 'type' in response_lower or 'enter' in response_lower:
            return {"action_type": "type", "target_element": "input", "additional_input": ""}
        elif 'navigate' in response_lower:
            return {"action_type": "navigate", "target_element": "browser"}
        elif 'finish' in response_lower or 'complete' in response_lower:
            return {"action_type": "finish", "target_element": "task"}
        else:
            return {"action_type": "wait", "target_element": "unknown"}