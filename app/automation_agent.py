import time
from typing import Dict, List, Tuple, Any, Optional
from app.input_processor import InputProcessor
from app.category_matcher import CategoryMatcher
from app.task_planner import TaskPlanner
from app.browser_controller import BrowserController
from utils.ui_analyzer import UIAnalyzer
from utils.step_executor import StepExecutor

class AutomationAgent:
    def __init__(self):
        self.input_processor = InputProcessor()
        self.category_matcher = CategoryMatcher()
        self.task_planner = TaskPlanner()
        self.browser_controller = None
        self.ui_analyzer = None
        self.step_executor = None
        self.current_task = None
        self.execution_status = "idle"
        
    def initialize_browser(self):
        """
        Initialize browser and related components
        """
        if not self.browser_controller:
            self.browser_controller = BrowserController()
            self.ui_analyzer = UIAnalyzer(self.browser_controller)
            self.step_executor = StepExecutor(self.browser_controller)
    
    def process_task(self, text_input: Optional[str] = None, 
                    audio_file: Optional[str] = None, 
                    transcript_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Main method to process and execute automation tasks
        """
        try:
            # Step 1: Process input
            processed_text = self.input_processor.process_input(text_input, audio_file, transcript_file)
            if not processed_text:
                return {
                    "status": "error",
                    "message": "No valid input provided",
                    "category": "",
                    "steps": [],
                    "screenshot": None
                }
            
            # Step 2: Match category
            category_id, confidence = self.category_matcher.match_category(processed_text)
            category_info = self.category_matcher.get_category_info(category_id)
            
            # Step 3: Generate task steps
            task_steps = self.task_planner.generate_task_steps(category_id, processed_text)
            
            # Step 4: Initialize browser if needed
            self.initialize_browser()
            
            # Step 5: Execute initial action
            initial_action = self.category_matcher.get_initial_action(category_id)
            execution_result = self._execute_initial_action(initial_action)
            
            # Step 6: Execute remaining steps
            final_result = self._execute_task_steps(task_steps, processed_text)
            
            return {
                "status": "completed",
                "message": f"Task executed successfully. Category: {category_info['name']} (confidence: {confidence:.2f})",
                "category": f"{category_info['name']} ({category_id})",
                "steps": self._format_execution_log(),
                "screenshot": final_result.get("final_screenshot"),
                "original_input": processed_text
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Task execution failed: {str(e)}",
                "category": "",
                "steps": self._format_execution_log(),
                "screenshot": None
            }
    
    def _execute_initial_action(self, action: str) -> Dict[str, Any]:
        """
        Execute the initial action based on category
        """
        try:
            if action == "open_gmail":
                screenshot = self.browser_controller.open_gmail()
                return {"success": True, "screenshot": screenshot}
            elif action == "open_browser":
                screenshot = self.browser_controller.open_google()
                return {"success": True, "screenshot": screenshot}
            elif action == "perform_search":
                screenshot = self.browser_controller.open_google()
                return {"success": True, "screenshot": screenshot}
            else:
                screenshot = self.browser_controller.open_google()
                return {"success": True, "screenshot": screenshot}
                
        except Exception as e:
            return {"success": False, "error": str(e), "screenshot": None}
    
    def _execute_task_steps(self, steps: List[str], original_input: str) -> Dict[str, Any]:
        """
        Execute all task steps sequentially
        """
        results = []
        final_screenshot = None
        
        for i, step in enumerate(steps):
            try:
                # Skip initial browser/gmail opening steps if already done
                if i == 0 and any(keyword in step.lower() for keyword in ["open browser", "open gmail", "navigate to google"]):
                    continue
                
                # Get current page context
                page_context = self.ui_analyzer.analyze_current_page()
                
                # Execute the step
                success, message, screenshot = self.step_executor.execute_step(step, page_context)
                
                results.append({
                    "step": step,
                    "success": success,
                    "message": message,
                    "screenshot": screenshot
                })
                
                final_screenshot = screenshot
                
                # Wait between steps
                time.sleep(0.2)
                
                # Handle manual input scenarios
                if not success and "manual" in message.lower():
                    print(f"Manual input required for step: {step}")
                    self.browser_controller.wait_for_manual_input(10)
                
            except Exception as e:
                results.append({
                    "step": step,
                    "success": False,
                    "message": f"Step execution error: {str(e)}",
                    "screenshot": None
                })
        
        return {
            "step_results": results,
            "final_screenshot": final_screenshot,
            "total_steps": len(steps),
            "successful_steps": sum(1 for r in results if r["success"])
        }
    
    def _format_execution_log(self) -> str:
        """
        Format execution log for display
        """
        if not self.step_executor:
            return "No execution log available"
        
        log_entries = self.step_executor.get_execution_log()
        if not log_entries:
            return "No steps executed yet"
        
        formatted_log = []
        for i, entry in enumerate(log_entries, 1):
            formatted_log.append(f"{i}. {entry}")
        
        return "\n".join(formatted_log)
    
    def get_current_status(self) -> Dict[str, Any]:
        """
        Get current automation status
        """
        return {
            "status": self.execution_status,
            "browser_active": self.browser_controller is not None,
            "current_url": self.browser_controller.get_current_url() if self.browser_controller else "",
            "steps_executed": len(self.step_executor.get_execution_log()) if self.step_executor else 0
        }
    
    def take_screenshot(self) -> str:
        """
        Take screenshot of current state
        """
        if self.browser_controller:
            return self.browser_controller.take_screenshot("manual_screenshot")
        return None
    
    def analyze_current_ui(self) -> Dict[str, Any]:
        """
        Analyze current UI state
        """
        if self.ui_analyzer:
            return self.ui_analyzer.analyze_current_page()
        return {}
    
    def stop_automation(self):
        """
        Stop automation and cleanup
        """
        self.execution_status = "stopped"
        if self.browser_controller:
            self.browser_controller.close()
            self.browser_controller = None
        
        if self.step_executor:
            self.step_executor.clear_log()
    
    def __del__(self):
        """
        Cleanup on object destruction
        """
        try:
            self.stop_automation()
        except:
            pass