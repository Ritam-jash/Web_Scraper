#!/usr/bin/env python3
"""
Google Maps Scraper - Main Entry Point
Run this file to start scraping Google Maps business data
"""

import sys
import argparse
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.logger import setup_logger
from config.settings import Settings

def main():
    """Main function to run the Google Maps scraper"""
    
    # Set up logging
    logger = setup_logger("gmaps_scraper", "INFO" if not Settings.DEBUG_MODE else "DEBUG")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Google Maps Business Scraper')
    parser.add_argument('--search', '-s', type=str, required=True,
                       help='Search query (e.g., "restaurants in Kolkata")')
    parser.add_argument('--max-results', '-m', type=int, default=Settings.MAX_BUSINESSES_PER_SEARCH,
                       help='Maximum number of businesses to scrape')
    parser.add_argument('--headless', action='store_true',
                       help='Run browser in headless mode')
    parser.add_argument('--output-format', '-f', choices=['csv', 'json', 'excel', 'all'],
                       default='csv', help='Output format')
    
    args = parser.parse_args()
    
    logger.info("="*50)
    logger.info("🚀 Starting Google Maps Scraper")
    logger.info("="*50)
    logger.info(f"Search Query: {args.search}")
    logger.info(f"Max Results: {args.max_results}")
    logger.info(f"Headless Mode: {args.headless or Settings.HEADLESS_MODE}")
    logger.info(f"Output Format: {args.output_format}")
    logger.info("="*50)
    
    try:
        # TODO: Phase 2 - Import and run the actual scraper
        # from src.scraper.gmaps_scraper import GMapsScraper
        # scraper = GMapsScraper()
        # results = scraper.scrape(args.search, args.max_results)
        
        logger.info("✅ Phase 1 setup completed successfully!")
        logger.info("📝 Next: Implement the scraper classes in Phase 2")
        
    except KeyboardInterrupt:
        logger.info("⏹️  Scraping interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
