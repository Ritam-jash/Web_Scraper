import time
import random
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class RateLimiter:
    """Control the rate of requests to avoid being blocked"""
    
    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time: Optional[float] = None
        self.request_count = 0
    
    def wait(self, custom_delay: Optional[float] = None):
        """Wait for appropriate time before next request"""
        current_time = time.time()
        
        if custom_delay is not None:
            delay = custom_delay
        else:
            # Random delay between min and max
            delay = random.uniform(self.min_delay, self.max_delay)
        
        if self.last_request_time is not None:
            time_since_last = current_time - self.last_request_time
            if time_since_last < delay:
                sleep_time = delay - time_since_last
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
        
        # Log every 10 requests
        if self.request_count % 10 == 0:
            logger.info(f"Completed {self.request_count} requests")
    
    def reset(self):
        """Reset the rate limiter"""
        self.last_request_time = None
        self.request_count = 0
        logger.debug("Rate limiter reset")