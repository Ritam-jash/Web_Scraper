
# ==================== src/scraper/browser_manager.py ====================
import os
import random
import time
import logging
from typing import Optional, List
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

from config.settings import Settings

logger = logging.getLogger(__name__)

class BrowserManager:
    """Manages Chrome browser instance with anti-detection features"""
    
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.user_agent = UserAgent()
        self.proxy_list: List[str] = []
        self.current_proxy_index = 0
        self.load_proxies()
    
    def load_proxies(self):
        """Load proxy list from file if enabled"""
        if Settings.USE_PROXY and os.path.exists(Settings.PROXY_LIST_FILE):
            try:
                with open(Settings.PROXY_LIST_FILE, 'r') as f:
                    self.proxy_list = [line.strip() for line in f if line.strip()]
                logger.info(f"Loaded {len(self.proxy_list)} proxies")
            except Exception as e:
                logger.warning(f"Could not load proxies: {e}")
    
    def get_chrome_options(self) -> Options:
        """Configure Chrome options with anti-detection measures"""
        options = Options()
        
        # Basic settings
        if Settings.HEADLESS_MODE:
            options.add_argument('--headless')
        
        options.add_argument(f'--window-size={getattr(Settings, "WINDOW_WIDTH", 1920)},{getattr(Settings, "WINDOW_HEIGHT", 1080)}')
        
        # Anti-detection arguments
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Random user agent
        if getattr(Settings, 'ROTATE_USER_AGENT', True):
            user_agent = self.user_agent.random
            options.add_argument(f'--user-agent={user_agent}')
            logger.debug(f"Using User Agent: {user_agent}")
        
        # Proxy settings
        if Settings.USE_PROXY and self.proxy_list:
            proxy = self.get_next_proxy()
            if proxy:
                options.add_argument(f'--proxy-server={proxy}')
                logger.info(f"Using proxy: {proxy}")
        
        # Additional stealth options
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins-discovery')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--no-default-browser-check')
        options.add_argument('--no-first-run')
        options.add_argument('--disable-default-apps')
        
        return options
    
    def get_next_proxy(self) -> Optional[str]:
        """Get next proxy from the list"""
        if not self.proxy_list:
            return None
        
        proxy = self.proxy_list[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)
        return proxy
    
    def create_driver(self) -> webdriver.Chrome:
        """Create and configure Chrome driver"""
        try:
            service = Service(ChromeDriverManager().install())
            options = self.get_chrome_options()
            
            driver = webdriver.Chrome(service=service, options=options)
            
            # Set timeouts
            driver.set_page_load_timeout(Settings.PAGE_LOAD_TIMEOUT)
            driver.implicitly_wait(Settings.BROWSER_TIMEOUT)
            
            # Execute stealth script
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Chrome driver created successfully")
            return driver
            
        except Exception as e:
            logger.error(f"Failed to create Chrome driver: {e}")
            raise
    
    def start_browser(self) -> webdriver.Chrome:
        """Start browser session"""
        if self.driver:
            self.close_browser()
        
        self.driver = self.create_driver()
        return self.driver
    
    def close_browser(self):
        """Close browser session"""
        if self.driver:
            try:
                self.driver.quit()
                logging.info("Browser closed successfully")
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
            finally:
                self.driver = None
    
    def wait_for_element(self, by: By, value: str, timeout: int = None) -> bool:
        """Wait for element to be present"""
        if not self.driver:
            return False
        
        timeout = timeout or getattr(Settings, 'ELEMENT_WAIT_TIMEOUT', 10)
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            return False
    
    def safe_click(self, element, delay: float = None):
        """Click element with human-like delay"""
        try:
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            
            # Wait a bit
            delay = delay or Settings.CLICK_DELAY
            time.sleep(random.uniform(delay * 0.5, delay * 1.5))
            
            # Click using JavaScript if regular click fails
            try:
                element.click()
            except:
                self.driver.execute_script("arguments[0].click();", element)
            
            logger.debug("Element clicked successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to click element: {e}")
            return False