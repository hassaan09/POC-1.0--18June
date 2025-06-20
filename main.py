import json
import time
from config import Config
from gui_capturer.ui_capturer import UICapturer
from retriever.task_retriever import TaskRetriever
from llm_agent.agent import LLMAgent
from executor.action_executor import ActionExecutor
from utils.logger import Logger
from ui.ui_server import UIServer

class GUIAutomationAgent:
    def __init__(self):
        Config.create_directories()
        self.logger = Logger()
        self.ui_capturer = UICapturer()
        self.retriever = TaskRetriever()
        self.llm_agent = LLMAgent()
        self.executor = ActionExecutor()
        self.step_count = 0
        
    def run_automation(self, instruction):
        """Main automation loop"""
        self.logger.log(f"Starting automation: {instruction}")
        self.step_count = 0
        
        try:
            # Initialize browser
            self.executor.initialize_browser()
            
            while True:
                self.step_count += 1
                self.logger.log(f"Step {self.step_count}")
                
                # Capture current UI state
                screenshot_path, ui_tree = self.ui_capturer.capture_state(self.step_count)
                
                # Retrieve similar examples
                retrieved_examples = self.retriever.retrieve_similar(instruction)
                
                # Get LLM suggestion
                action_suggestion = self.llm_agent.get_action_suggestion(
                    instruction, ui_tree, retrieved_examples, screenshot_path
                )
                
                self.logger.log(f"Action suggestion: {action_suggestion}")
                
                # Execute action
                if action_suggestion['action_type'] == 'finish':
                    self.logger.log("Task completed")
                    break
                elif action_suggestion['action_type'] == 'wait':
                    self.logger.log("Waiting for manual input...")
                    input("Press Enter to continue...")
                    continue
                
                success = self.executor.execute_action(action_suggestion)
                if not success:
                    self.logger.log("Action execution failed")
                    break
                
                time.sleep(2)  # Brief pause between actions
                
        except Exception as e:
            self.logger.log(f"Error in automation: {str(e)}")
        finally:
            self.executor.cleanup()
            
    def process_instruction(self, instruction, audio_file=None):
        """Process user instruction and start automation"""
        if audio_file:
            # Audio transcription would go here
            instruction = "Transcribed: " + instruction
            
        result = {
            "status": "started",
            "instruction": instruction,
            "steps_completed": 0
        }
        
        # Run automation in separate thread for production
        self.run_automation(instruction)
        
        return result

def main():
    agent = GUIAutomationAgent()
    ui_server = UIServer(agent)
    ui_server.launch()

if __name__ == "__main__":
    main()