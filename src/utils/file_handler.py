import os
import json
import csv
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    """Handle file operations for different output formats"""
    
    def __init__(self, output_dir: str = "data/output"):
        self.output_dir = output_dir
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create necessary directories"""
        directories = [
            self.output_dir,
            f"{self.output_dir}/csv",
            f"{self.output_dir}/json",
            f"{self.output_dir}/excel"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")
    
    def generate_filename(self, search_query: str, file_format: str) -> str:
        """Generate filename based on search query and timestamp"""
        # Clean search query for filename
        clean_query = "".join(c for c in search_query if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_query = clean_query.replace(' ', '_').lower()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gmaps_{clean_query}_{timestamp}.{file_format}"
        
        return filename
    
    def clean_field(self, value):
        if value is None:
            return ""
        # Remove problematic characters (like the Google Maps icon)
        value = str(value).replace('', '').replace('\n', ' ').replace('\r', ' ')
        # Optionally, remove other non-printable/control characters
        value = ''.join(c for c in value if c.isprintable())
        return value
    
    def save_to_csv(self, businesses: List[Dict[str, Any]], search_query: str) -> str:
        """Save businesses data to CSV file"""
        if not businesses:
            logger.warning("No businesses data to save to CSV")
            return ""
        
        filename = self.generate_filename(search_query, "csv")
        filepath = os.path.join(self.output_dir, "csv", filename)
        
        try:
            # Clean all fields in all business records
            cleaned_businesses = [
                {k: self.clean_field(v) for k, v in business.items()}
                for business in businesses
            ]
            df = pd.DataFrame(cleaned_businesses)
            df.to_csv(filepath, index=False, encoding='utf-8', quoting=csv.QUOTE_MINIMAL)
            logger.info(f"Saved {len(businesses)} businesses to CSV: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            return ""
    
    def save_to_json(self, businesses: List[Dict[str, Any]], search_query: str) -> str:
        """Save businesses data to JSON file"""
        if not businesses:
            logger.warning("No businesses data to save to JSON")
            return ""
        
        filename = self.generate_filename(search_query, "json")
        filepath = os.path.join(self.output_dir, "json", filename)
        
        try:
            output_data = {
                "search_query": search_query,
                "scraped_at": datetime.now().isoformat(),
                "total_businesses": len(businesses),
                "businesses": businesses
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(businesses)} businesses to JSON: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
            return ""
    
    def save_to_excel(self, businesses: List[Dict[str, Any]], search_query: str) -> str:
        """Save businesses data to Excel file with formatting"""
        if not businesses:
            logger.warning("No businesses data to save to Excel")
            return ""
        
        filename = self.generate_filename(search_query, "xlsx")
        filepath = os.path.join(self.output_dir, "excel", filename)
        
        try:
            df = pd.DataFrame(businesses)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Businesses', index=False)
                
                # Get workbook and worksheet
                worksheet = writer.sheets['Businesses']
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)  # Max width of 50
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            logger.info(f"Saved {len(businesses)} businesses to Excel: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Error saving to Excel: {e}")
            return ""
    
    def save_businesses(self, businesses: List[Dict[str, Any]], search_query: str, 
                       formats: List[str] = None) -> Dict[str, str]:
        """Save businesses in multiple formats"""
        if formats is None:
            formats = ['csv', 'json']
        
        saved_files = {}
        
        for format_type in formats:
            if format_type.lower() == 'csv':
                filepath = self.save_to_csv(businesses, search_query)
                if filepath:
                    saved_files['csv'] = filepath
            
            elif format_type.lower() == 'json':
                filepath = self.save_to_json(businesses, search_query)
                if filepath:
                    saved_files['json'] = filepath
            
            elif format_type.lower() == 'excel':
                filepath = self.save_to_excel(businesses, search_query)
                if filepath:
                    saved_files['excel'] = filepath
        
        return saved_files