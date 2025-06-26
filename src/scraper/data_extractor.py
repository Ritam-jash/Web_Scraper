import re
import time
import logging
from typing import Optional, Dict, Any, List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime

from src.models.business import Business
from config.selectors import GoogleMapsSelectors

logger = logging.getLogger(__name__)

class DataExtractor:
    """Extract business data from Google Maps pages"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def extract_business_data(self, search_query: str = "") -> Optional[Business]:
        """Extract all available business data from current page"""
        try:
            # Wait for page to load
            time.sleep(2)
            
            business_data = {
                'search_query': search_query,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Extract basic information
            business_data.update(self._extract_basic_info())
            
            # Extract contact information
            business_data.update(self._extract_contact_info())
            
            # Extract rating and reviews
            business_data.update(self._extract_rating_info())
            
            # Extract additional details
            business_data.update(self._extract_additional_info())
            
            # Extract coordinates
            business_data.update(self._extract_coordinates())
            
            # Create Business object
            business = Business(**business_data)
            logger.debug(f"Extracted data for: {business.name}")
            
            return business
            
        except Exception as e:
            logger.error(f"Error extracting business data: {e}")
            return None
    
    def _extract_basic_info(self) -> Dict[str, Any]:
        """Extract basic business information"""
        data = {}
        
        # Business name
        name_selectors = [
            "h1.DUwDvf",
            "h1[data-attrid='title']",
            "h1.x3AX1-LfntMc-header-title-title",
            "h1",
            ".x3AX1-LfntMc-header-title-title"
        ]
        
        data['name'] = self._get_text_by_selectors(name_selectors, "Business name")
        
        # Business category
        category_selectors = [
            "button[jsaction*='category']",
            ".DkEaL",
            ".W4Efsd:first-child .W4Efsd",
            "button[data-value='Directions'] + div .W4Efsd"
        ]
        
        data['category'] = self._get_text_by_selectors(category_selectors, "Category")
        
        return data
    
    def _extract_contact_info(self) -> Dict[str, Any]:
        """Extract contact information"""
        data = {}
        
        # Address
        address_selectors = [
            "button[data-item-id='address']",
            ".Io6YTe",
            "button[data-item-id='address'] .Io6YTe",
            ".rogA2c .Io6YTe"
        ]
        
        data['address'] = self._get_text_by_selectors(address_selectors, "Address")
        
        # Phone number
        phone_selectors = [
            "button[data-item-id*='phone']",
            ".rogA2c[data-item-id*='phone']",
            "button[aria-label*='phone'] .Io6YTe",
            "span[role='text'][aria-label*='phone']"
        ]
        
        phone_text = self._get_text_by_selectors(phone_selectors, "Phone")
        if phone_text:
            # Clean phone number
            data['phone'] = self._clean_phone_number(phone_text)
        
        # Website
        website_selectors = [
            "a[data-item-id='authority']",
            "a[href*='http']:not([href*='google.com']):not([href*='maps'])",
            ".CsEnBe a[href*='http']",
            "a[aria-label*='website']"
        ]
        
        website_element = self._get_element_by_selectors(website_selectors)
        if website_element:
            try:
                data['website'] = website_element.get_attribute('href')
                logger.debug(f"Found website: {data['website']}")
            except:
                pass
        
        return data
    
    def _extract_rating_info(self) -> Dict[str, Any]:
        """Extract rating and review information"""
        data = {}
        
        # Rating
        rating_selectors = [
            ".MW4etd",
            ".ceNzKf",
            "span.MW4etd",
            ".F7nice span"
        ]
        
        rating_text = self._get_text_by_selectors(rating_selectors, "Rating")
        if rating_text:
            try:
                # Extract number from rating text
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    data['rating'] = float(rating_match.group(1))
            except:
                pass
        
        # Review count
        review_selectors = [
            ".UY7F9",
            "button[aria-label*='reviews'] .UY7F9",
            ".F7nice .UY7F9",
            "span.UY7F9"
        ]
        
        review_text = self._get_text_by_selectors(review_selectors, "Reviews")
        if review_text:
            try:
                # Extract number from review text (e.g., "(1,234)" -> 1234)
                review_match = re.search(r'[\(]?(\d+[\d,]*)\)?', review_text.replace(',', ''))
                if review_match:
                    data['reviews_count'] = int(review_match.group(1).replace(',', ''))
            except:
                pass
        
        return data
    
    def _extract_additional_info(self) -> Dict[str, Any]:
        """Extract additional business information"""
        data = {}
        
        # Business hours
        hours_selectors = [
            ".t39EBf",
            "[data-item-id='oh'] .t39EBf",
            ".OqCZI .t39EBf",
            ".eXlrNe .t39EBf"
        ]
        
        # Try to find hours information
        hours_elements = []
        for selector in hours_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    hours_elements = elements
                    break
            except:
                continue
        
        if hours_elements:
            try:
                hours_text = []
                for element in hours_elements[:7]:  # Max 7 days
                    text = element.text.strip()
                    if text:
                        hours_text.append(text)
                
                if hours_text:
                    data['hours'] = '; '.join(hours_text)
                    logger.debug(f"Found hours: {data['hours']}")
            except Exception as e:
                logger.debug(f"Error extracting hours: {e}")
        
        # Price range
        price_selectors = [
            ".mgr77e",
            "[aria-label*='Price'] .mgr77e",
            ".RWPxGd .mgr77e"
        ]
        
        data['price_range'] = self._get_text_by_selectors(price_selectors, "Price range")
        
        return data
    
    def _extract_coordinates(self) -> Dict[str, Any]:
        """Extract latitude and longitude from URL"""
        data = {}
        
        try:
            current_url = self.driver.current_url
            
            # Look for coordinates in URL patterns
            # Pattern: @lat,lng,zoom or !3d<lat>!4d<lng>
            patterns = [
                r'@(-?\d+\.?\d*),(-?\d+\.?\d*),',
                r'!3d(-?\d+\.?\d*)!4d(-?\d+\.?\d*)',
                r'/(-?\d+\.?\d*),(-?\d+\.?\d*)/'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, current_url)
                if match:
                    lat, lng = match.groups()
                    data['coordinates'] = (float(lat), float(lng))
                    logger.debug(f"Found coordinates: {data['coordinates']}")
                    break
        
        except Exception as e:
            logger.debug(f"Error extracting coordinates: {e}")
        
        return data
    
    def _get_text_by_selectors(self, selectors: List[str], field_name: str = "") -> Optional[str]:
        """Try multiple selectors to get text content"""
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text:
                    logger.debug(f"Found {field_name}: {text}")
                    return text
            except NoSuchElementException:
                continue
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue
        
        logger.debug(f"Could not find {field_name}")
        return None
    
    def _get_element_by_selectors(self, selectors: List[str]):
        """Try multiple selectors to get element"""
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                return element
            except NoSuchElementException:
                continue
            except Exception:
                continue
        return None
    
    def _clean_phone_number(self, phone_text: str) -> str:
        """Clean and format phone number"""
        if not phone_text:
            return ""
        
        # Remove common prefixes and suffixes
        phone = phone_text.replace('Call', '').replace('Phone:', '').strip()
        
        # Keep only digits, spaces, hyphens, parentheses, and plus signs
        phone = re.sub(r'[^0-9\s\-\(\)\+]', '', phone)
        
        return phone.strip()
