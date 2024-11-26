from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import datetime

@dataclass
class PropertyDetails:
    zpid: str
    address: str
    price: float
    bedrooms: float
    bathrooms: float
    square_feet: float
    lot_size: Optional[float] = None
    year_built: Optional[int] = None
    property_type: Optional[str] = None
    zestimate: Optional[float] = None
    rent_estimate: Optional[float] = None
    last_sold_price: Optional[float] = None
    last_sold_date: Optional[datetime] = None
    days_on_zillow: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photos: Optional[List[str]] = None

    def to_dict(self) -> Dict:
        """Convert property details to dictionary format."""
        return {
            'zpid': self.zpid,
            'address': self.address,
            'price': self.price,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'square_feet': self.square_feet,
            'lot_size': self.lot_size,
            'year_built': self.year_built,
            'property_type': self.property_type,
            'zestimate': self.zestimate,
            'rent_estimate': self.rent_estimate,
            'last_sold_price': self.last_sold_price,
            'last_sold_date': self.last_sold_date.isoformat() if self.last_sold_date else None,
            'days_on_zillow': self.days_on_zillow,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'photos': self.photos
        }

@dataclass
class PropertySearchCriteria:
    """Search criteria for property search."""
    location: str
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_beds: Optional[int] = None
    max_beds: Optional[int] = None
    min_baths: Optional[float] = None
    max_baths: Optional[float] = None
    min_sqft: Optional[float] = None
    max_sqft: Optional[float] = None
    property_type: Optional[str] = None
    min_year_built: Optional[int] = None
    max_year_built: Optional[int] = None
    max_days_on_zillow: Optional[int] = None
    status_type: str = "ForSale"
    sort_by: str = "Price_Low_High"

    def to_api_params(self) -> Dict[str, str]:
        """Convert search criteria to API parameters."""
        params = {'location': self.location}
        
        if self.min_price is not None:
            params['minPrice'] = str(int(self.min_price))
        if self.max_price is not None:
            params['maxPrice'] = str(int(self.max_price))
        if self.min_beds is not None:
            params['minBeds'] = str(self.min_beds)
        if self.max_beds is not None:
            params['maxBeds'] = str(self.max_beds)
        if self.min_baths is not None:
            params['minBaths'] = str(self.min_baths)
        if self.max_baths is not None:
            params['maxBaths'] = str(self.max_baths)
        if self.min_sqft is not None:
            params['minSqft'] = str(int(self.min_sqft))
        if self.max_sqft is not None:
            params['maxSqft'] = str(int(self.max_sqft))
        if self.property_type:
            params['propertyType'] = self.property_type
        if self.min_year_built is not None:
            params['minYearBuilt'] = str(self.min_year_built)
        if self.max_year_built is not None:
            params['maxYearBuilt'] = str(self.max_year_built)
        if self.max_days_on_zillow is not None:
            params['daysOnZillow'] = str(self.max_days_on_zillow)
        
        params['status'] = self.status_type
        params['sort'] = self.sort_by
        
        return params
