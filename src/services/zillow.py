import os
import time
import requests
from typing import Dict, List, Optional
from functools import lru_cache
from dotenv import load_dotenv

from src.models.property import PropertyDetails, PropertySearchCriteria

load_dotenv()

class ZillowAPIError(Exception):
    """Custom exception for Zillow API errors."""
    pass

class ZillowService:
    """Service class for interacting with the Zillow API."""
    
    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_ZILLOW_API_KEY")
        if not self.api_key:
            raise ValueError("RAPIDAPI_ZILLOW_API_KEY environment variable is not set")
            
        self.base_url = "https://zillow-com1.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com",
            "X-RapidAPI-Key": self.api_key
        }
        
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """Make a request to the Zillow API with rate limiting and error handling."""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            # Rate limiting - wait 1 second between requests
            time.sleep(1)
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise ZillowAPIError(f"API request failed: {str(e)}")
        except ValueError as e:
            raise ZillowAPIError(f"Invalid JSON response: {str(e)}")
    
    def search_properties(self, criteria: PropertySearchCriteria) -> List[PropertyDetails]:
        """Search for properties using the given criteria."""
        endpoint = "propertyExtendedSearch"
        params = criteria.to_api_params()
        
        try:
            response = self._make_request(endpoint, params)
            
            if not response or 'props' not in response:
                return []
                
            properties = []
            for prop_data in response['props']:
                try:
                    property_details = PropertyDetails.from_zillow_api(prop_data)
                    properties.append(property_details)
                except (ValueError, KeyError) as e:
                    # Log the error but continue processing other properties
                    print(f"Error processing property data: {str(e)}")
                    continue
                    
            return properties
            
        except ZillowAPIError as e:
            print(f"Search failed: {str(e)}")
            return []
    
    @lru_cache(maxsize=100)
    def get_property_details(self, zpid: str) -> Optional[PropertyDetails]:
        """Get detailed information about a specific property."""
        endpoint = "property"
        params = {"zpid": zpid}
        
        try:
            response = self._make_request(endpoint, params)
            return PropertyDetails.from_zillow_api(response)
            
        except ZillowAPIError as e:
            print(f"Failed to get property details: {str(e)}")
            return None
    
    @lru_cache(maxsize=100)
    def get_property_images(self, zpid: str) -> List[str]:
        """Get images for a specific property."""
        endpoint = "images"
        params = {"zpid": zpid}
        
        try:
            response = self._make_request(endpoint, params)
            return response.get('images', [])
            
        except ZillowAPIError as e:
            print(f"Failed to get property images: {str(e)}")
            return []
    
    def get_rent_estimate(self, property_details: PropertyDetails) -> Optional[float]:
        """Get rent estimate for a property."""
        endpoint = "rental/estimatePrice"
        params = {
            "propertyType": property_details.property_type,
            "address": property_details.address,
            "bedrooms": str(int(property_details.bedrooms)),
            "bathrooms": str(property_details.bathrooms)
        }
        
        try:
            response = self._make_request(endpoint, params)
            return float(response.get('rent', 0))
            
        except (ZillowAPIError, ValueError) as e:
            print(f"Failed to get rent estimate: {str(e)}")
            return None
