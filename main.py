#!/usr/bin/env python3
"""
Google Maps Scraper - Main Entry Point
Run this file to start scraping Google Maps business data
"""

import sys
import argparse
from pathlib import Path
import pandas as pd
import os
from rapidfuzz import fuzz
import re

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
        # Phase 2 - Import and run the actual scraper
        from src.scraper.gmaps_scraper import GMapsScraper

        # Update settings from CLI args if provided
        Settings.HEADLESS_MODE = args.headless or Settings.HEADLESS_MODE
        Settings.OUTPUT_FORMAT = args.output_format or Settings.OUTPUT_FORMAT
        Settings.MAX_BUSINESSES_PER_SEARCH = args.max_results or Settings.MAX_BUSINESSES_PER_SEARCH

        scraper = GMapsScraper()
        results = scraper.scrape(args.search, args.max_results)

        if results:
            logger.info(f"\n✅ Scraping completed! {len(results)} businesses scraped.")
            logger.info(f"\n📁 Output files saved in: {Settings.OUTPUT_DIR}")

            # === Post-processing: Filter and clean data, then save to Excel ===
            # Find the latest CSV file in the output directory
            csv_dir = os.path.join(Settings.OUTPUT_DIR, 'csv')
            csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
            if csv_files:
                latest_csv = max([os.path.join(csv_dir, f) for f in csv_files], key=os.path.getctime)
                df = pd.read_csv(latest_csv)
                # Only keep desired columns
                filtered = df[['name', 'phone', 'address', 'website']].copy()
                # Advanced website filtering: fuzzy domain matching and TLD/domain pattern checks
                def clean_name(name):
                    return re.sub(r'[^a-z0-9]', '', str(name).lower())

                def extract_domain(url):
                    if pd.isna(url) or not isinstance(url, str) or url.strip() == '':
                        return ''
                    domain = re.sub(r'https?://(www\.)?', '', url).split('/')[0]
                    return domain

                def is_good_tld(domain):
                    # Accept only common business TLDs
                    good_tlds = ['.com', '.in', '.net', '.org', '.co', '.biz', '.info']
                    return any(domain.endswith(tld) for tld in good_tlds)

                def is_bad_pattern(domain, url):
                    # Exclude known aggregator/third-party domains and subpages
                    bad_domains = [
                        'google.com', 'swiggy.com', 'zomato.com', 'tripadvisor.com',
                        'facebook.com', 'instagram.com', 'about/products?tab=lh',
                        'maps.google', 'goo.gl', 'bit.ly', 'wa.link', 'airmenus.in',
                        'phoenixpalladium.com', 'magicpin.in', 'openrice.com', 'justdial.com',
                        'yelp.com', 'dineout.co.in', 'ubereats.com', 'foodpanda.com', 'faasos.com',
                        'zabihah.com', 'timescity.com', 'eazydiner.com', 'orderfoodonline.in',
                        'eatigo.com', 'restroapp.com', 'tablein.com', 'eatfresh.com', 'foursquare.com',
                        'trip.com', 'makemytrip.com', 'cleartrip.com', 'ixigo.com', 'redbus.in',
                        'agoda.com', 'booking.com', 'expedia.com', 'hotels.com', 'oyorooms.com',
                        'goibibo.com', 'trivago.in', 'hostelworld.com', 'airbnb.com', 'stayzilla.com',
                        'instagram.com', 'facebook.com', 'twitter.com', 'linkedin.com', 'youtube.com',
                    ]
                    if any(bad in domain for bad in bad_domains):
                        return True
                    # Exclude URLs with aggregator-like subpages
                    bad_paths = ['/order/', '/booking/', '/reviews/', '/city/', '/restaurants/', '/menu/', '/reserve/', '/dineout/', '/delivery/']
                    if any(path in url for path in bad_paths):
                        return True
                    return False

                def is_fuzzy_match(domain, business_name):
                    # Use only the main part of the domain (before first dot)
                    main_domain = domain.split('.')[0]
                    name_clean = clean_name(business_name)
                    domain_clean = clean_name(main_domain)
                    # Accept if domain is a substring of name or vice versa
                    if domain_clean in name_clean or name_clean in domain_clean:
                        return True
                    # Use rapidfuzz for fuzzy matching (lowered threshold)
                    score = fuzz.partial_ratio(domain_clean, name_clean)
                    return score >= 70

                def advanced_website_filter(url, business_name):
                    domain = extract_domain(url)
                    if not domain or not is_good_tld(domain):
                        return 'None'
                    if is_bad_pattern(domain, url):
                        return 'None'
                    if is_fuzzy_match(domain, business_name):
                        return url
                    return 'None'

                filtered['website'] = [
                    advanced_website_filter(x, n)
                    for x, n in zip(filtered['website'], filtered['name'])
                ]
                # Save to Excel in the 'excel' output directory
                excel_dir = os.path.join(Settings.OUTPUT_DIR, 'excel')
                os.makedirs(excel_dir, exist_ok=True)
                excel_filename = os.path.basename(latest_csv).replace('.csv', '_filtered.xlsx')
                excel_path = os.path.join(excel_dir, excel_filename)
                filtered.to_excel(excel_path, index=False)
                logger.info(f"Filtered Excel file saved: {excel_path}")
        else:
            logger.warning("No businesses were scraped.")

    except KeyboardInterrupt:
        logger.info("⏹️  Scraping interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
