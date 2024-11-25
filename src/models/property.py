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
    
    @classmethod
    def from_zillow_api(cls, api_response: Dict) -> 'PropertyDetails':
        """Create a PropertyDetails instance from Zillow API response."""
        return cls(
            zpid=str(api_response.get('zpid', '')),
            address=api_response.get('address', {}).get('streetAddress', ''),
            price=float(api_response.get('price', 0)),
            bedrooms=float(api_response.get('bedrooms', 0)),
            bathrooms=float(api_response.get('bathrooms', 0)),
            square_feet=float(api_response.get('livingArea', 0)),
            lot_size=float(api_response.get('lotAreaValue', 0)),
            year_built=int(api_response.get('yearBuilt', 0)) if api_response.get('yearBuilt') else None,
            property_type=api_response.get('homeType', ''),
            zestimate=float(api_response.get('zestimate', 0)),
            rent_estimate=float(api_response.get('rentZestimate', 0)),
            last_sold_price=float(api_response.get('lastSoldPrice', 0)),
            last_sold_date=datetime.strptime(api_response.get('lastSoldDate', ''), '%Y-%m-%d') 
                if api_response.get('lastSoldDate') else None,
            days_on_zillow=int(api_response.get('daysOnZillow', 0)),
            latitude=float(api_response.get('latitude', 0)),
            longitude=float(api_response.get('longitude', 0)),
            photos=api_response.get('photos', [])
        )
    
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
            'last_sold_date': self.last_sold_date.strftime('%Y-%m-%d') if self.last_sold_date else None,
            'days_on_zillow': self.days_on_zillow,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'photos': self.photos
        }

@dataclass
class PropertySearchCriteria:
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
    
    def to_api_params(self) -> Dict:
        """Convert search criteria to API parameters."""
        params = {
            "location": self.location,
            "status_type": self.status_type,
            "sort": self.sort_by,
        }
        
        if self.min_price is not None:
            params["minPrice"] = str(int(self.min_price))
        if self.max_price is not None:
            params["maxPrice"] = str(int(self.max_price))
        if self.min_beds is not None:
            params["bedsMin"] = str(self.min_beds)
        if self.max_beds is not None:
            params["bedsMax"] = str(self.max_beds)
        if self.min_baths is not None:
            params["bathsMin"] = str(self.min_baths)
        if self.max_baths is not None:
            params["bathsMax"] = str(self.max_baths)
        if self.min_sqft is not None:
            params["sqftMin"] = str(int(self.min_sqft))
        if self.max_sqft is not None:
            params["sqftMax"] = str(int(self.max_sqft))
        if self.property_type is not None:
            params["home_type"] = self.property_type
        if self.min_year_built is not None:
            params["buildYearMin"] = str(self.min_year_built)
        if self.max_year_built is not None:
            params["buildYearMax"] = str(self.max_year_built)
        if self.max_days_on_zillow is not None:
            params["daysOn"] = str(self.max_days_on_zillow)
            
        return params
