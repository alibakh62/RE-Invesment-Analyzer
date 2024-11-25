"""Zillow API service with improved error handling and caching."""
import os
import time
import json
from typing import Dict, List, Optional, Any
from functools import lru_cache
import requests
from datetime import datetime, timedelta
from pathlib import Path

from src.config.settings import API_CONFIG, CACHE_CONFIG
from src.config.logging import logger, log_api_request, log_api_error
from src.models.property import PropertyDetails, PropertySearchCriteria

class ZillowAPIException(Exception):
    """Custom exception for Zillow API errors."""
    pass

class RateLimitException(ZillowAPIException):
    """Exception for rate limiting."""
    pass

class ZillowService:
    """Service for interacting with Zillow API with caching and error handling."""
    
    def __init__(self):
        self.api_key = API_CONFIG['ZILLOW_API_KEY']
        if not self.api_key:
            raise ValueError("Zillow API key not found in environment variables")
        
        self.base_url = API_CONFIG['ZILLOW_BASE_URL']
        self.headers = {
            "X-RapidAPI-Host": API_CONFIG['ZILLOW_API_HOST'],
            "X-RapidAPI-Key": self.api_key
        }
        self.cache_dir = CACHE_CONFIG['CACHE_DIR']
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _make_request(self, endpoint: str, params: Dict[str, Any], cache_key: Optional[str] = None) -> Dict:
        """Make API request with caching and error handling."""
        url = f"{self.base_url}/{endpoint}"
        
        # Try to get from cache first
        if cache_key:
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data
        
        try:
            log_api_request(endpoint, params)
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 429:
                raise RateLimitException("API rate limit exceeded")
            
            response.raise_for_status()
            data = response.json()
            
            # Cache the response if cache_key provided
            if cache_key:
                self._save_to_cache(cache_key, data)
            
            # Rate limiting - wait between requests
            time.sleep(1)
            
            return data
            
        except RateLimitException:
            log_api_error(endpoint, "Rate limit exceeded")
            raise
        except requests.exceptions.RequestException as e:
            log_api_error(endpoint, str(e))
            raise ZillowAPIException(f"API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            log_api_error(endpoint, f"Invalid JSON response: {str(e)}")
            raise ZillowAPIException("Invalid API response format")
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the cache file path for a given key."""
        return self.cache_dir / f"{cache_key}.json"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Retrieve data from cache if valid."""
        cache_file = self._get_cache_path(cache_key)
        
        if not cache_file.exists():
            return None
            
        # Check cache age
        file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        if file_age > timedelta(seconds=CACHE_CONFIG['MAX_AGE']):
            return None
            
        try:
            with cache_file.open('r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def _save_to_cache(self, cache_key: str, data: Dict) -> None:
        """Save data to cache."""
        cache_file = self._get_cache_path(cache_key)
        try:
            with cache_file.open('w') as f:
                json.dump(data, f)
        except IOError as e:
            logger.warning(f"Failed to cache data: {str(e)}")
    
    @lru_cache(maxsize=100)
    def get_property_details(self, zpid: str) -> Optional[PropertyDetails]:
        """Get detailed information about a specific property."""
        try:
            cache_key = f"property_{zpid}"
            response = self._make_request("property", {"zpid": zpid}, cache_key)
            return PropertyDetails.from_zillow_api(response)
        except ZillowAPIException as e:
            logger.error(f"Failed to get property details for {zpid}: {str(e)}")
            return None
    
    def search_properties(self, criteria: PropertySearchCriteria) -> List[PropertyDetails]:
        """Search for properties using the given criteria."""
        try:
            params = criteria.to_api_params()
            cache_key = f"search_{hash(frozenset(params.items()))}"
            
            response = self._make_request("propertyExtendedSearch", params, cache_key)
            
            if not response or 'props' not in response:
                return []
            
            properties = []
            for prop_data in response.get('props', []):
                try:
                    property_details = PropertyDetails.from_zillow_api(prop_data)
                    properties.append(property_details)
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error processing property data: {str(e)}")
                    continue
            
            return properties
            
        except ZillowAPIException as e:
            logger.error(f"Property search failed: {str(e)}")
            return []
    
    @lru_cache(maxsize=100)
    def get_property_images(self, zpid: str) -> List[str]:
        """Get images for a specific property."""
        try:
            cache_key = f"images_{zpid}"
            response = self._make_request("images", {"zpid": zpid}, cache_key)
            return response.get('images', [])
        except ZillowAPIException as e:
            logger.error(f"Failed to get property images for {zpid}: {str(e)}")
            return []
    
    def get_rent_estimate(self, property_details: PropertyDetails) -> Optional[float]:
        """Get rent estimate for a property."""
        try:
            params = {
                "propertyType": property_details.property_type,
                "address": property_details.address,
                "beds": str(int(property_details.bedrooms)),
                "baths": str(property_details.bathrooms)
            }
            
            cache_key = f"rent_{hash(frozenset(params.items()))}"
            response = self._make_request("rentEstimate", params, cache_key)
            
            return float(response.get('rent', 0))
        except (ZillowAPIException, ValueError) as e:
            logger.error(f"Failed to get rent estimate: {str(e)}")
            return None
    
    def search_by_mls(self, mls_number: str) -> Optional[PropertyDetails]:
        """Search for a property by MLS number."""
        try:
            cache_key = f"mls_{mls_number}"
            response = self._make_request("propertyByMls", {"mls": mls_number}, cache_key)
            return PropertyDetails.from_zillow_api(response)
        except ZillowAPIException as e:
            logger.error(f"Failed to find property with MLS {mls_number}: {str(e)}")
            return None
