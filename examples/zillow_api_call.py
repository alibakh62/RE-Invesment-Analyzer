"""Example of using the Zillow API service."""
import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from src.services.zillow_service import ZillowService

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('zillow_example')

def get_property_details(address: str) -> dict:
    """Get property details from Zillow API."""
    try:
        # Initialize Zillow service
        zillow = ZillowService()
        
        # Get property details
        logger.info(f"Fetching property details for: {address}")
        property_details = zillow.get_property_details(address)
        
        if not property_details:
            logger.error("Could not find property details")
            return None
        
        # Print property details
        print("\nProperty Details")
        print("-" * 50)
        print(f"Address: {property_details.address}")
        print(f"Price: ${property_details.price:,.2f}")
        print(f"Zestimate: ${property_details.zestimate:,.2f}")
        print(f"Monthly Rent Estimate: ${property_details.rent_estimate:,.2f}")
        print(f"Bedrooms: {property_details.bedrooms}")
        print(f"Bathrooms: {property_details.bathrooms}")
        print(f"Square Feet: {property_details.square_feet:,.0f}")
        print(f"Year Built: {property_details.year_built}")
        
        # Get comparable properties
        logger.info("Fetching comparable properties")
        comps = zillow.get_comparable_properties(
            property_details.zpid,
            radius_miles=1,
            limit=5
        )
        
        if comps:
            print("\nComparable Properties")
            print("-" * 50)
            for i, comp in enumerate(comps, 1):
                print(f"\nProperty {i}:")
                print(f"Address: {comp.address}")
                print(f"Price: ${comp.price:,.2f}")
                print(f"Square Feet: {comp.square_feet:,.0f}")
                print(f"Price/SqFt: ${comp.price/comp.square_feet:.2f}")
        
        return property_details
        
    except Exception as e:
        logger.error(f"Error getting property details: {str(e)}", exc_info=True)
        raise

def main():
    """Run example."""
    # Check if Zillow API key is set
    if not os.getenv("RAPIDAPI_ZILLOW_API_KEY"):
        print("Error: RAPIDAPI_ZILLOW_API_KEY environment variable not set")
        print("\nPlease set your RapidAPI Zillow API key:")
        print("export RAPIDAPI_ZILLOW_API_KEY='your-api-key'")
        print("\nYou can get your API key from: https://rapidapi.com/apimaker/api/zillow-com1/")
        return
    
    # Get address from user
    address = input("\nEnter property address: ")
    
    try:
        get_property_details(address)
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()