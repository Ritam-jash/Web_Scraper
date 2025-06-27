# ==================== src/scraper/gmaps_scraper.py ====================
import time
import random
import logging
from typing import List, Optional, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

from src.scraper.browser_manager import BrowserManager
from src.scraper.data_extractor import DataExtractor
from src.models.business import Business
from src.utils.rate_limiter import RateLimiter
from src.utils.file_handler import FileHandler
from config.settings import Settings
from config.selectors import GoogleMapsSelectors

logger = logging.getLogger(__name__)

class GMapsScraper:
    """Main Google Maps scraper class"""
    
    def __init__(self):
        self.browser_manager = BrowserManager()
        self.rate_limiter = RateLimiter(
            Settings.MIN_DELAY_BETWEEN_REQUESTS,
            Settings.MAX_DELAY_BETWEEN_REQUESTS
        )
        self.file_handler = FileHandler(Settings.OUTPUT_DIR)
        self.driver = None
        self.data_extractor = None
        self.scraped_businesses: List[Business] = []
        self.failed_businesses: List[str] = []
    
    def scrape(self, search_query: str, max_results: int = None) -> List[Business]:
        """Main scraping method"""
        max_results = max_results or Settings.MAX_BUSINESSES_PER_SEARCH
        
        try:
            logger.info(f"🔍 Starting scrape for: '{search_query}'")
            logger.info(f"📊 Target: {max_results} businesses")
            
            # Start browser
            self.driver = self.browser_manager.start_browser()
            self.data_extractor = DataExtractor(self.driver)
            
            # Navigate to Google Maps
            self._navigate_to_google_maps()
            
            # Perform search
            self._perform_search(search_query)
            
            # Load all business listings
            business_links = self._load_business_listings(max_results)
            
            if not business_links:
                logger.warning("❌ No business listings found")
                return []
            
            logger.info(f"📋 Found {len(business_links)} business listings")
            
            # Extract data from each business
            self._extract_businesses_data(business_links, search_query)
            
            # Save results
            if self.scraped_businesses:
                self._save_results(search_query)
            
            self._log_summary()
            
            return self.scraped_businesses
            
        except KeyboardInterrupt:
            logger.info("⏹️  Scraping interrupted by user")
            if self.scraped_businesses:
                self._save_results(search_query, suffix="_interrupted")
            raise
            
        except Exception as e:
            logger.error(f"❌ Critical error during scraping: {e}")
            raise
            
        finally:
            self._cleanup()
    
    def _navigate_to_google_maps(self):
        """Navigate to Google Maps homepage"""
        logger.info("🌐 Navigating to Google Maps...")
        
        try:
            self.driver.get(Settings.GOOGLE_MAPS_URL)
            
            # Wait for search box to load
            wait = WebDriverWait(self.driver, 20)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, GoogleMapsSelectors.SEARCH_BOX)))
            
            logger.info("✅ Google Maps loaded successfully")
            
        except TimeoutException:
            logger.error("❌ Timeout waiting for Google Maps to load")
            raise
        except Exception as e:
            logger.error(f"❌ Error navigating to Google Maps: {e}")
            raise
    
    def _perform_search(self, search_query: str):
        """Perform search on Google Maps"""
        logger.info(f"🔍 Searching for: '{search_query}'")
        
        try:
            # Find search box
            search_box = self.driver.find_element(By.CSS_SELECTOR, GoogleMapsSelectors.SEARCH_BOX)
            
            # Clear and enter search query
            search_box.clear()
            search_box.send_keys(search_query)
            
            # Add human-like delay
            time.sleep(random.uniform(1, 2))
            
            # Press Enter or click search button
            search_box.send_keys(Keys.ENTER)
            
            # Wait for results to load
            wait = WebDriverWait(self.driver, 15)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='main']")))
            
            # Additional wait for results to fully load
            time.sleep(3)
            
            logger.info("✅ Search completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error performing search: {e}")
            raise
    
    def _load_business_listings(self, max_results: int) -> List[str]:
        """Load and collect business listing URLs"""
        logger.info("📜 Loading business listings...")
        
        business_links = []
        scroll_attempts = 0
        max_scroll_attempts = 200
        no_new_results_count = 0
        
        try:
            while len(business_links) < max_results and scroll_attempts < max_scroll_attempts:
                scroll_attempts += 1
                previous_count = len(business_links)
                
                # Find all business links on current page
                current_links = self._extract_business_links()
                
                # Add new unique links
                for link in current_links:
                    if link not in business_links:
                        business_links.append(link)
                
                # Log progress
                if len(business_links) > previous_count:
                    logger.info(f"📊 Found {len(business_links)} businesses so far...")
                    no_new_results_count = 0
                else:
                    no_new_results_count += 1
                
                # Break if no new results for several attempts
                if no_new_results_count >= 5:
                    logger.info("🔚 No more new results found")
                    break
                
                # Check if we have enough results
                if len(business_links) >= max_results:
                    logger.info(f"🎯 Reached target of {max_results} businesses")
                    break
                
                # Scroll to load more results
                self._scroll_results_panel()
                
                # Try clicking 'Next' or 'More results' button if present
                self._click_next_or_more_results_button()
                
                # Rate limiting
                self.rate_limiter.wait(Settings.SCROLL_PAUSE_TIME)
            
            # Limit to max_results
            business_links = business_links[:max_results]
            
            logger.info(f"✅ Collected {len(business_links)} business listings")
            return business_links
            
        except Exception as e:
            logger.error(f"❌ Error loading business listings: {e}")
            return business_links
    
    def _extract_business_links(self) -> List[str]:
        """Extract business links from current page"""
        links = []
        
        try:
            # Try different selectors for business links
            selectors = [
                "a[href*='/maps/place/']",
                "div[role='main'] a[data-value='Directions']",
                "a[aria-label][href*='maps']",
                ".Nv2PK a[href*='/maps/place/']"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        href = element.get_attribute('href')
                        if href and '/maps/place/' in href and href not in links:
                            links.append(href)
                    
                    if links:
                        break
                        
                except Exception as e:
                    logger.debug(f"Error with selector {selector}: {e}")
                    continue
            
            return links
            
        except Exception as e:
            logger.error(f"Error extracting business links: {e}")
            return []
    
    def _scroll_results_panel(self):
        """Scroll the results panel to load more listings"""
        try:
            # Try to find and scroll the results panel
            panel_selectors = [
                "div[role='main']",
                ".m6QErb",
                ".siAUzd",
                "#pane"
            ]
            
            panel = None
            for selector in panel_selectors:
                try:
                    panel = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if panel:
                # Scroll using JavaScript
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight",
                    panel
                )
                
                # Also try scrolling with Page Down
                panel.send_keys(Keys.PAGE_DOWN)
                
            else:
                # Fallback: scroll the entire page
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
        except Exception as e:
            logger.debug(f"Error scrolling results panel: {e}")
    
    def _extract_businesses_data(self, business_links: List[str], search_query: str):
        """Extract data from each business"""
        logger.info(f"🔍 Extracting data from {len(business_links)} businesses...")
        
        for i, link in enumerate(business_links, 1):
            try:
                logger.info(f"📊 Processing business {i}/{len(business_links)}")
                start_time = time.time()  # Start timing
                
                # Navigate to business page
                self.driver.get(link)
                
                # Use WebDriverWait for the first business, sleep for others
                if i == 1:
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-item-id*='phone'], .rogA2c[data-item-id*='phone'], button[aria-label*='phone'] .Io6YTe, span[role='text'][aria-label*='phone']"))
                        )
                    except Exception as e:
                        logger.warning(f"Phone number element not found for first business: {e}")
                else:
                    time.sleep(random.uniform(2, 4))
                
                # Extract business data
                business = self.data_extractor.extract_business_data(search_query)
                
                if business and business.name:
                    business.google_maps_url = link
                    self.scraped_businesses.append(business)
                    logger.info(f"✅ {i}: {business.name}")
                else:
                    self.failed_businesses.append(link)
                    logger.warning(f"❌ {i}: Failed to extract data from {link}")
                
                # Rate limiting
                self.rate_limiter.wait()
                
                # If this is the last business, add a short delay to ensure all data is loaded and written
                if i == len(business_links):
                    time.sleep(2)
                
                # Log time taken for this business
                end_time = time.time()
                duration = end_time - start_time
                logger.info(f"⏱️ Time taken for business {i}: {duration:.2f} seconds")
            except Exception as e:
                logger.error(f"❌ Error processing business {i}: {e}")
                self.failed_businesses.append(link)
                continue
    
    def _save_results(self, search_query: str, suffix: str = ""):
        """Save scraped results to files"""
        logger.info("💾 Saving results...")
        
        try:
            # Convert businesses to dictionaries
            businesses_data = [business.to_dict() for business in self.scraped_businesses]
            
            # Determine output formats
            output_formats = []
            if Settings.OUTPUT_FORMAT == 'all':
                output_formats = ['csv', 'json', 'excel']
            else:
                output_formats = [Settings.OUTPUT_FORMAT]
            
            # Save files
            saved_files = self.file_handler.save_businesses(
                businesses_data, 
                search_query + suffix, 
                output_formats
            )
            
            # Log saved files
            for format_type, filepath in saved_files.items():
                logger.info(f"✅ Saved {format_type.upper()}: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Error saving results: {e}")
    
    def _log_summary(self):
        """Log scraping summary"""
        logger.info("="*50)
        logger.info("📊 SCRAPING SUMMARY")
        logger.info("="*50)
        logger.info(f"✅ Successfully scraped: {len(self.scraped_businesses)} businesses")
        logger.info(f"❌ Failed to scrape: {len(self.failed_businesses)} businesses")
        logger.info(f"📈 Success rate: {len(self.scraped_businesses)/(len(self.scraped_businesses)+len(self.failed_businesses))*100:.1f}%")
        logger.info("="*50)
    
    def _cleanup(self):
        """Clean up resources"""
        logger.info("🧹 Cleaning up...")
        
        if self.browser_manager:
            self.browser_manager.close_browser()
        
        logger.info("✅ Cleanup completed")

    def _click_next_or_more_results_button(self):
        """Try to click 'Next' or 'More results' button if present to load more listings"""
        try:
            # Common selectors for next/more results buttons
            button_selectors = [
                "button[aria-label=' Next page '], button[aria-label='Next page']",  # Next page button
                "button[aria-label*='More results']",  # More results button
                "button[jsaction*='pane.paginationSection.nextPage']",  # Pagination next
                "div[role='button'][aria-label*='Next']",  # Generic next button
                "span:contains('Next'), span:contains('More results')"  # Fallback
            ]
            for selector in button_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            logger.info("Clicked 'Next' or 'More results' button.")
                            time.sleep(2)  # Wait for new results to load
                            return True
                except Exception as e:
                    logger.debug(f"Error trying selector {selector} for next/more results: {e}")
            return False
        except Exception as e:
            logger.debug(f"Error clicking next/more results button: {e}")
            return False