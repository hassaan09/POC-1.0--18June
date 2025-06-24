import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait # Not strictly used, but common
from selenium.webdriver.common.action_chains import ActionChains # Not strictly used, but common
from webdriver_manager.chrome import ChromeDriverManager
import glob # Import glob for robust path finding

# --- Configuration (mimicking your Config class) ---
class Config:
    SCREENSHOT_DIR = "screenshots"
    IMPLICIT_WAIT = 10
    EXPLICIT_WAIT = 20
    CHROME_HEADLESS = False # Set to True if you want to test headless mode

# --- Test Function for Browser Initialization ---
def initialize_browser_test():
    print("--- Starting Browser Initialization Test ---")
    driver = None
    try:
        chrome_options = Options()

        # Anti-detection arguments (from your previously working setup)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Headless mode setup based on Config
        if Config.CHROME_HEADLESS:
            chrome_options.add_argument('--headless=new') # Use 'new' for modern Chrome headless
            chrome_options.add_argument('--window-size=1920,1080') # Recommended for headless
        
        # Ensure the screenshots directory exists (good practice from your project)
        os.makedirs(Config.SCREENSHOT_DIR, exist_ok=True)
        
        # --- CRITICAL PATH FIX LOGIC ---
        print("Attempting to install/locate ChromeDriver using webdriver_manager...")
        # Get the path that webdriver_manager provides.
        # This path might point to the directory, or sometimes an incorrect file like THIRD_PARTY_NOTICES.
        driver_candidate_path = ChromeDriverManager().install()

        actual_driver_path = None
        
        # Check if the returned path is not directly the .exe
        if not driver_candidate_path.lower().endswith('.exe'):
            print(f"WebDriverManager returned a path that doesn't end with '.exe': {driver_candidate_path}")
            
            # Case 1: The path is a directory (most common when webdriver_manager is working correctly)
            # Search for 'chromedriver.exe' within this directory
            found_exe = glob.glob(os.path.join(driver_candidate_path, 'chromedriver.exe'))
            
            if not found_exe:
                # Case 2: The path is pointing to a file *other than* chromedriver.exe
                # (like your observed THIRD_PARTY_NOTICES.chromedriver)
                # In this case, the actual .exe is likely in the parent directory.
                parent_dir = os.path.dirname(driver_candidate_path)
                found_exe = glob.glob(os.path.join(parent_dir, 'chromedriver.exe'))
            
            if found_exe:
                actual_driver_path = found_exe[0] # Take the first found executable
                print(f"Successfully located chromedriver.exe at: {actual_driver_path}")
            else:
                raise FileNotFoundError(
                    f"Could not find 'chromedriver.exe' in expected locations. "
                    f"WebDriverManager returned: {driver_candidate_path}"
                )
        else:
            actual_driver_path = driver_candidate_path # Path was already correct (ending with .exe)
            print(f"WebDriverManager returned a direct path to chromedriver.exe: {actual_driver_path}")

        # --- END CRITICAL PATH FIX LOGIC ---

        print(f"Final ChromeDriver path used: {actual_driver_path}")
        service = Service(executable_path=actual_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.implicitly_wait(Config.IMPLICIT_WAIT)
        
        # Maximize window only if not in headless mode
        if not Config.CHROME_HEADLESS:
            driver.maximize_window()
        
        # JavaScript to remove automation indicators
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        driver.get("https://www.google.com")
        print("Browser initialized and navigated to Google successfully!")
        time.sleep(5) # Keep the browser open for 5 seconds to observe
        
    except Exception as e:
        print(f"\n--- ERROR during browser initialization test ---")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        print("Please check the console output for specific details.")
    finally:
        if driver:
            print("Closing browser...")
            driver.quit()
        print("--- Browser Initialization Test Finished ---")

if __name__ == "__main__":
    initialize_browser_test()