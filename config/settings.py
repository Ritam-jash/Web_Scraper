import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # Browser Settings
    HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'False').lower() == 'true'
    BROWSER_TIMEOUT = int(os.getenv('BROWSER_TIMEOUT', '30'))
    PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', '20'))
    
    # Scraping Settings
    SCROLL_PAUSE_TIME = float(os.getenv('SCROLL_PAUSE_TIME', '2'))
    CLICK_DELAY = float(os.getenv('CLICK_DELAY', '1.5'))
    MAX_BUSINESSES_PER_SEARCH = int(os.getenv('MAX_BUSINESSES', '100'))
    
    # Rate Limiting
    MIN_DELAY_BETWEEN_REQUESTS = float(os.getenv('MIN_DELAY', '1'))
    MAX_DELAY_BETWEEN_REQUESTS = float(os.getenv('MAX_DELAY', '3'))
    
    # Output Settings
    OUTPUT_FORMAT = os.getenv('OUTPUT_FORMAT', 'csv')  # csv, json, excel
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'data/output')
    
    # Proxy Settings
    USE_PROXY = os.getenv('USE_PROXY', 'False').lower() == 'true'
    PROXY_LIST_FILE = os.getenv('PROXY_LIST_FILE', 'data/proxies/proxy_list.txt')
    
    # Debug Settings
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'True').lower() == 'true'
    SAVE_SCREENSHOTS = False  # Disabled by default for performance
    
    # Google Maps URLs and Selectors
    GOOGLE_MAPS_URL = "https://www.google.com/maps"