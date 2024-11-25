"""Example usage of the caching module."""
from src.utils.caching import cache, cached
from src.models.property import PropertyDetails
from src.services.zillow_service import ZillowService

# Example 1: Basic cache usage
def get_property_details(property_id: str) -> PropertyDetails:
    """Get property details with caching."""
    # Try to get from cache
    cached_property = cache.get(f"property:{property_id}")
    if cached_property:
        return cached_property
    
    # Get from API and cache
    zillow = ZillowService()
    property_details = zillow.get_property_details(property_id)
    cache.set(f"property:{property_id}", property_details, expire=3600)  # Cache for 1 hour
    return property_details

# Example 2: Using the cache decorator
@cached(prefix='property_search', expire=1800)  # Cache for 30 minutes
def search_properties(location: str, min_price: float, max_price: float) -> list:
    """Search properties with caching."""
    zillow = ZillowService()
    return zillow.search_properties(location, min_price, max_price)

# Example 3: Custom key function
def create_search_key(location: str, **kwargs) -> str:
    """Create a custom cache key for property search."""
    key_parts = [location.lower()]
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")
    return ':'.join(key_parts)

@cached(prefix='property_search', expire=1800, key_func=create_search_key)
def advanced_property_search(
    location: str,
    min_price: float = None,
    max_price: float = None,
    min_beds: int = None,
    max_beds: int = None,
    property_type: str = None
) -> list:
    """Advanced property search with custom cache key."""
    zillow = ZillowService()
    return zillow.advanced_search(
        location=location,
        min_price=min_price,
        max_price=max_price,
        min_beds=min_beds,
        max_beds=max_beds,
        property_type=property_type
    )

# Example 4: Cache clearing
def clear_property_cache(property_id: str = None):
    """Clear property cache."""
    if property_id:
        # Clear specific property
        cache.delete(f"property:{property_id}")
    else:
        # Clear all cache
        cache.clear()

# Example usage
if __name__ == "__main__":
    # Example 1: Basic cache usage
    property_details = get_property_details("123456")
    print(f"Got property details: {property_details.address}")
    
    # Example 2: Decorator usage
    properties = search_properties("San Francisco, CA", 500000, 1000000)
    print(f"Found {len(properties)} properties")
    
    # Example 3: Advanced search with custom key
    results = advanced_property_search(
        location="Seattle, WA",
        min_price=400000,
        max_price=800000,
        min_beds=2,
        property_type="SingleFamily"
    )
    print(f"Found {len(results)} matching properties")
    
    # Example 4: Cache clearing
    clear_property_cache("123456")  # Clear specific property
    clear_property_cache()  # Clear all cache
