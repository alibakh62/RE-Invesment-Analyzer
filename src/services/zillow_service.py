"""Zillow API service with improved error handling and caching."""
import os
import time
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from functools import lru_cache
import requests
from datetime import datetime, timedelta
from pathlib import Path

from src.models.property import PropertyDetails, PropertySearchCriteria

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ZillowAPIException(Exception):
    """Custom exception for Zillow API errors."""
    pass

class RateLimitException(ZillowAPIException):
    """Exception for rate limiting."""
    pass

class ZillowService:
    """Service for interacting with Zillow API with caching and error handling."""
    
    BASE_URL = "https://zillow-com1.p.rapidapi.com"
    
    def __init__(self):
        """Initialize the Zillow service."""
        self.api_key = os.getenv('RAPIDAPI_ZILLOW_API_KEY')
        if not self.api_key:
            raise ValueError("RAPIDAPI_ZILLOW_API_KEY not found in environment variables")
        
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'zillow-com1.p.rapidapi.com'
        }
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to the Zillow API."""
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            logger.debug(f"Making API request to {url} with params: {params}")
            response = requests.get(url, headers=self.headers, params=params)
            
            # Log the response for debugging
            logger.debug(f"Response status code: {response.status_code}")
            logger.debug(f"Response headers: {response.headers}")
            logger.debug(f"Response content: {response.text[:500]}...")  # Log first 500 chars
            
            response.raise_for_status()
            
            if response.status_code == 429:
                raise RateLimitException("Rate limit exceeded")
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise ZillowAPIException(f"API request failed: {str(e)}")
    
    def _search_properties(self, location: str) -> Tuple[bool, Union[str, List[Dict[str, Any]]]]:
        """
        Search for properties by location.
        Returns a tuple (is_exact_address, result) where:
        - is_exact_address is True if an exact address was provided
        - result is either a zpid string (for exact address) or a list of properties (for general location)
        """
        try:
            logger.debug(f"Searching properties for location: {location}")
            params = {
                "location": location,
                "page": "1"
            }
            
            response = self._make_request("propertyExtendedSearch", params)
            
            if not response:
                logger.debug("No response from propertyExtendedSearch")
                return False, []
                
            if 'props' not in response:
                logger.debug(f"No 'props' in response. Full response: {response}")
                return False, []
            
            props = response.get('props', [])
            if not props:
                logger.debug("No properties found in response")
                return False, []
            
            logger.debug(f"Found {len(props)} properties")
            
            # If it's an exact address, we'll typically get one result
            if len(props) == 1:
                zpid = str(props[0].get('zpid', ''))
                logger.debug(f"Found single property with zpid: {zpid}")
                return True, zpid
            
            # If it's a general location, return all properties
            logger.debug(f"Found multiple properties: {len(props)}")
            return False, props
            
        except Exception as e:
            logger.error(f"Property search failed: {str(e)}")
            return False, []
    
    def search_properties(self, criteria: PropertySearchCriteria) -> List[PropertyDetails]:
        """Search for properties using the given criteria."""
        try:
            logger.debug(f"Searching properties with criteria: {criteria.__dict__}")
            params = {
                "location": criteria.location,
                "page": "1"
            }
            
            # Only add optional parameters if they have values
            if criteria.status_type:
                params["status_type"] = criteria.status_type
            if criteria.property_type:
                params["home_type"] = criteria.property_type
            if criteria.sort_by:
                params["sort"] = criteria.sort_by
            if criteria.min_price is not None:
                params["minPrice"] = str(int(criteria.min_price))
            if criteria.max_price is not None:
                params["maxPrice"] = str(int(criteria.max_price))
            if criteria.min_beds is not None:
                params["bedsMin"] = str(criteria.min_beds)
            if criteria.max_beds is not None:
                params["bedsMax"] = str(criteria.max_beds)
            if criteria.min_baths is not None:
                params["bathsMin"] = str(criteria.min_baths)
            if criteria.max_baths is not None:
                params["bathsMax"] = str(criteria.max_baths)
            if criteria.min_sqft is not None:
                params["sqftMin"] = str(int(criteria.min_sqft))
            if criteria.max_sqft is not None:
                params["sqftMax"] = str(int(criteria.max_sqft))
            if criteria.min_year_built is not None:
                params["buildYearMin"] = str(criteria.min_year_built)
            if criteria.max_year_built is not None:
                params["buildYearMax"] = str(criteria.max_year_built)
            if criteria.max_days_on_zillow is not None:
                params["daysOn"] = str(criteria.max_days_on_zillow)
            
            # Step 1: Get list of properties with zpids
            response = self._make_request("propertyExtendedSearch", params)
            
            if not response or 'props' not in response:
                logger.debug("No properties found matching criteria")
                return []
            
            # Step 2: Get full details for each property
            properties = []
            for prop_data in response.get('props', []):
                try:
                    zpid = str(prop_data.get('zpid', ''))
                    if not zpid:
                        logger.warning("Property data missing zpid")
                        continue
                    
                    logger.debug(f"Getting details for property with zpid: {zpid}")
                    property_details = self.get_property_details_by_zpid(zpid)
                    if property_details:
                        properties.append(property_details)
                    else:
                        logger.warning(f"Could not get details for property with zpid: {zpid}")
                except Exception as e:
                    logger.warning(f"Error processing property data: {str(e)}")
                    continue
            
            logger.debug(f"Found {len(properties)} properties with details")
            return properties
            
        except Exception as e:
            logger.error(f"Property search failed: {str(e)}")
            return []
    
    def get_property_details(self, address: str) -> Optional[PropertyDetails]:
        """
        Get property details by address.
        This is a two-step process:
        1. First, get the zpid using propertyExtendedSearch endpoint
        2. Then, get the full property details using the property endpoint
        """
        try:
            logger.debug(f"Getting property details for address: {address}")
            
            # Step 1: Get zpid using propertyExtendedSearch
            params = {"location": address}
            search_response = self._make_request("propertyExtendedSearch", params)
            
            if not search_response or 'props' not in search_response or not search_response['props']:
                logger.error(f"No properties found for address: {address}")
                return None
            
            # Get the zpid from the first property
            zpid = str(search_response['props'][0].get('zpid', ''))
            if not zpid:
                logger.error("Property found but no zpid available")
                return None
            
            logger.debug(f"Found property with zpid: {zpid}")
            
            # Step 2: Get full property details using the zpid
            return self.get_property_details_by_zpid(zpid)
            
        except Exception as e:
            logger.error(f"Error getting property details: {str(e)}")
            raise ZillowAPIException(f"Error getting property details: {str(e)}")
    
    def get_property_details_by_zpid(self, zpid: str) -> Optional[PropertyDetails]:
        """Get detailed property information using Zillow Property ID."""
        try:
            logger.debug(f"Getting property details for zpid: {zpid}")
            params = {"zpid": zpid}
            details = self._make_request("property", params)
            
            if not details:
                logger.debug("No details returned from property endpoint")
                return None
            
            # Get additional data
            logger.debug("Getting property images")
            images = self.get_property_images(zpid)
            
            logger.debug("Getting rent estimate")
            rent_estimate = self.get_rent_estimate(
                details.get('propertyType', ''),
                details.get('address', {}).get('streetAddress', ''),
                details.get('bedrooms', 0),
                details.get('bathrooms', 0)
            )
            
            property_details = PropertyDetails(
                zpid=zpid,
                address=details.get('address', {}).get('streetAddress', ''),
                price=float(details.get('price', 0)),
                bedrooms=float(details.get('bedrooms', 0)),
                bathrooms=float(details.get('bathrooms', 0)),
                square_feet=float(details.get('livingArea', 0)),
                lot_size=float(details.get('lotSize', 0)),
                year_built=int(details.get('yearBuilt', 0)),
                property_type=details.get('propertyType', ''),
                zestimate=float(details.get('zestimate', 0)),
                rent_estimate=float(rent_estimate) if rent_estimate else None,
                last_sold_price=float(details.get('lastSoldPrice', 0)),
                last_sold_date=datetime.fromtimestamp(details.get('lastSoldDate', 0)) if details.get('lastSoldDate') else None,
                days_on_zillow=int(details.get('daysOnZillow', 0)),
                latitude=float(details.get('latitude', 0)),
                longitude=float(details.get('longitude', 0)),
                photos=images
            )
            
            logger.debug(f"Successfully created PropertyDetails object: {property_details.__dict__}")
            return property_details
            
        except Exception as e:
            logger.error(f"Error getting property details: {str(e)}")
            return None
    
    def get_property_images(self, zpid: str) -> List[str]:
        """Get images for a specific property."""
        try:
            logger.debug(f"Getting images for zpid: {zpid}")
            params = {"zpid": zpid}
            response = self._make_request("images", params)
            images = response.get('images', [])
            logger.debug(f"Found {len(images)} images")
            return images
        except Exception as e:
            logger.error(f"Failed to get property images: {str(e)}")
            return []
    
    def get_rent_estimate(self, property_type: str, address: str, beds: int, baths: float) -> Optional[float]:
        """Get rent estimate for a property."""
        try:
            logger.debug(f"Getting rent estimate for: {address}")
            params = {
                "propertyType": property_type,
                "address": address,
                "beds": str(int(beds)),
                "baths": str(baths)
            }
            
            response = self._make_request("rentEstimate", params)
            rent = float(response.get('rent', 0))
            logger.debug(f"Rent estimate: ${rent:,.2f}")
            return rent
        except Exception as e:
            logger.error(f"Failed to get rent estimate: {str(e)}")
            return None
    
    def get_property_by_mls(self, mls_number: str) -> Optional[PropertyDetails]:
        """Search for a property by MLS number."""
        try:
            logger.debug(f"Searching for property with MLS number: {mls_number}")
            params = {"mls": mls_number}
            response = self._make_request("propertyByMls", params)
            
            if not response:
                logger.debug("No response from propertyByMls endpoint")
                return None
                
            if 'zpid' not in response:
                logger.debug(f"No zpid in response. Full response: {response}")
                return None
            
            zpid = str(response['zpid'])
            logger.debug(f"Found property with zpid: {zpid}")
            return self.get_property_details_by_zpid(zpid)
        except Exception as e:
            logger.error(f"Failed to find property with MLS {mls_number}: {str(e)}")
            return None
