from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
import json

@dataclass
class Business:
    """Data model for a business scraped from Google Maps"""
    
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    category: Optional[str] = None
    hours: Optional[str] = None
    price_range: Optional[str] = None
    coordinates: Optional[tuple] = None
    google_maps_url: Optional[str] = None
    search_query: Optional[str] = None
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert business object to dictionary"""
        data = asdict(self)
        if self.coordinates:
            data['latitude'] = self.coordinates[0]
            data['longitude'] = self.coordinates[1]
        else:
            data['latitude'] = None
            data['longitude'] = None
        data.pop('coordinates', None)
        return data
    
    def to_json(self) -> str:
        """Convert business object to JSON string"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    def __str__(self) -> str:
        return f"Business(name='{self.name}', address='{self.address}')"
