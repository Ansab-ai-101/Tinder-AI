import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from dotenv import load_dotenv

load_dotenv()

class TinderLogin:
    def __init__(self, headless=False):
        self.driver = None
        self.headless = headless
        self.google_email = os.getenv("GOOGLE_EMAIL")
        self.google_password = os.getenv("GOOGLE_PASSWORD")
    
    def start_driver(self):
        """Initialize undetected Chrome driver"""
        options = uc.ChromeOptions()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--disable-notifications")
        options.add_argument("--lang=en-US")
        
        self.driver = uc.Chrome(
            options=options,
            version_main=114  # Match your Chrome version
        )
        self.driver.maximize_window()
    
    def login_with_google(self):
        """Perform Google login to Tinder"""
        try:
            # Navigate to Tinder
            self.driver.get("https://tinder.com")
            
            # Wait and click login button
            login_btn = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//*[text()="Log in"]'))
            )
            login_btn.click()
            
            # Click Google login option
            google_btn = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//button[.//span[text()="Continue with Google"]]'))
            )
            google_btn.click()
            
            # Switch to Google login popup
            time.sleep(2)
            base_window = self.driver.window_handles[0]
            google_window = self.driver.window_handles[1]
            self.driver.switch_to.window(google_window)
            
            # Enter Google credentials
            email_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "identifierId"))
            )
            email_field.send_keys(self.google_email)
            
            next_btn = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "identifierNext"))
            )
            next_btn.click()
            
            # Enter password
            password_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.NAME, "Passwd"))
            )
            password_field.send_keys(self.google_password)
            
            password_next = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "passwordNext"))
            )
            password_next.click()
            
            # Switch back to Tinder window
            self.driver.switch_to.window(base_window)
            
            # Wait for login to complete and get auth token
            time.sleep(10)  # Allow time for login to complete
            
            # Get auth token from local storage
            auth_token = self.driver.execute_script(
                "return window.localStorage.getItem('TinderWeb/APIToken');"
            )
            
            return auth_token
            
        except Exception as e:
            print(f"Login failed: {e}")
            return None
        finally:
            if self.driver:
                self.driver.quit()
    
    def get_auth_token(self):
        """Public method to get auth token"""
        self.start_driver()
        return self.login_with_google()
