import json
import time
from config import Config
from gui_capturer.ui_capturer import UICapturer
from retriever.task_retriever import TaskRetriever
from llm_agent.agent import LLMAgent
from executor.action_executor import ActionExecutor
from utils.logger import Logger
from ui.ui_server import UIServer
from selenium import webdriver # ADDED: Import webdriver for initialization
from selenium.webdriver.chrome.service import Service # ADDED
from selenium.webdriver.chrome.options import Options # ADDED
from webdriver_manager.chrome import ChromeDriverManager # ADDED
import os # ADDED
import glob # ADDED


class GUIAutomationAgent:
    def __init__(self):
        Config.create_directories()
        self.logger = Logger()
        self.driver = None # ADDED: Centralized WebDriver instance
        self.ui_capturer = None # Will be initialized with shared driver
        self.retriever = TaskRetriever()
        self.llm_agent = LLMAgent()
        self.executor = None # Will be initialized with shared driver
        self.step_count = 0

    def _initialize_shared_browser(self):
        """Initializes and returns a single shared Chrome browser instance."""
        if self.driver:
            self.logger.log("Browser already initialized, skipping.")
            return self.driver

        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        if Config.CHROME_HEADLESS:
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--window-size=1920,1080')
        else:
            # For non-headless, ensure the window starts maximized
            chrome_options.add_argument('--start-maximized')

        os.makedirs(Config.SCREENSHOTS_DIR, exist_ok=True)

        # --- CRITICAL FIX START: Robust ChromeDriver Path Finding (Copied from Executor) ---
        self.logger.log("Main Agent: Attempting to install/locate ChromeDriver...")
        driver_candidate_path = ChromeDriverManager().install()

        actual_driver_path = None

        if not driver_candidate_path.lower().endswith('.exe'):
            self.logger.log(f"Main Agent: WebDriverManager returned an unexpected path: {driver_candidate_path}")

            found_exe = glob.glob(os.path.join(driver_candidate_path, 'chromedriver.exe'))

            if not found_exe:
                parent_dir = os.path.dirname(driver_candidate_path)
                found_exe = glob.glob(os.path.join(parent_dir, 'chromedriver.exe'))

            if found_exe:
                actual_driver_path = found_exe[0]
                self.logger.log(f"Main Agent: Corrected ChromeDriver path to: {actual_driver_path}")
            else:
                raise FileNotFoundError(
                    f"Main Agent: Could not find 'chromedriver.exe' after webdriver_manager install. "
                    f"WebDriverManager returned: {driver_candidate_path}"
                )
        else:
            actual_driver_path = driver_candidate_path
            self.logger.log(f"Main Agent: WebDriverManager returned a direct path to chromedriver.exe: {actual_driver_path}")

        self.logger.log(f"Main Agent: Final ChromeDriver path used: {actual_driver_path}")
        service = Service(executable_path=actual_driver_path)
        # --- CRITICAL FIX END ---

        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(Config.IMPLICIT_WAIT)

        # Hide webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        self.driver.get("https://www.google.com") # Start with Google homepage
        self.logger.log("Shared browser initialized and navigated to Google.")
        return self.driver

    def run_automation(self, instruction):
        """Main automation loop"""
        self.logger.log(f"Starting automation: {instruction}")
        self.step_count = 0

        try:
            # INITIALIZE THE SINGLE BROWSER INSTANCE AND PASS IT
            shared_driver = self._initialize_shared_browser()
            self.ui_capturer = UICapturer(shared_driver) # Pass driver to UICapturer
            self.executor = ActionExecutor(shared_driver) # Pass driver to ActionExecutor

            while True:
                self.step_count += 1
                self.logger.log(f"Step {self.step_count}")

                # Capture current UI state using the shared driver
                screenshot_path, ui_tree = self.ui_capturer.capture_state(self.step_count)

                # Retrieve similar examples
                retrieved_examples = self.retriever.retrieve_similar(instruction)

                # Get LLM suggestion
                action_suggestion = self.llm_agent.get_action_suggestion(
                    instruction, ui_tree, retrieved_examples, screenshot_path
                )

                self.logger.log(f"Action suggestion: {action_suggestion}")

                # Execute action using the shared driver
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

                time.sleep(Config.ACTION_DELAY) # CHANGED: Use a config value for delay
                                              # You'll need to add ACTION_DELAY to your config.py
                                              # e.g., ACTION_DELAY = 2

        except Exception as e:
            self.logger.log(f"Error in automation: {str(e)}")
        finally:
            # CLEANUP THE SINGLE SHARED BROWSER INSTANCE
            if self.driver:
                self.logger.log("Cleaning up shared browser.")
                self.driver.quit()
                self.driver = None # Reset the driver for potential new runs
            # No need to call cleanup on executor/capturer as they don't own the driver anymore.


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
        # For this refactor, we'll keep it direct for easier debugging.
        # If running in a UI server, consider threading this.
        self.run_automation(instruction)

        return result

def main():
    agent = GUIAutomationAgent()
    ui_server = UIServer(agent) # UIServer still takes the agent, which now manages the browser
    ui_server.launch()

if __name__ == "__main__":
    main()
