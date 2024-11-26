"""Example script demonstrating the use of the Zillow service."""
import os
import sys
import json

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.services.zillow_service import ZillowService
from src.models.property import PropertySearchCriteria

def format_property_details(details_dict: dict) -> None:
    """Format and print property details."""
    for key, value in details_dict.items():
        if value is not None and value != 0:  # Only show non-empty values
            if isinstance(value, float):
                if key in ['price', 'zestimate', 'rent_estimate', 'last_sold_price']:
                    print(f"{key.replace('_', ' ').title()}: ${value:,.2f}")
                else:
                    print(f"{key.replace('_', ' ').title()}: {value}")
            elif isinstance(value, list) and key == 'photos':
                print(f"Number of Photos: {len(value)}")
            else:
                print(f"{key.replace('_', ' ').title()}: {value}")

def get_property_details(zillow: ZillowService):
    """Get and display property details based on user input."""
    print("\n=== Property Details Lookup ===")
    print("1. Search by address")
    print("2. Search by MLS number")
    choice = input("Enter your choice (1-2): ").strip()
    
    if choice == "1":
        print("\nPlease enter the property address (e.g., '123 Main St, San Francisco, CA')")
        address = input("Address: ").strip()
        
        if not address:
            print("Error: Address cannot be empty")
            return
        
        try:
            print(f"\nLooking up details for: {address}")
            property_details = zillow.get_property_details(address)
            
            if property_details:
                print("\nProperty Details:")
                format_property_details(property_details.to_dict())
            else:
                print("Property not found")
        except Exception as e:
            print(f"Error getting property details: {e}")
            
    elif choice == "2":
        print("\nPlease enter the MLS number:")
        mls = input("MLS Number: ").strip()
        
        if not mls:
            print("Error: MLS number cannot be empty")
            return
        
        try:
            print(f"\nLooking up details for MLS: {mls}")
            property_details = zillow.get_property_by_mls(mls)
            
            if property_details:
                print("\nProperty Details:")
                format_property_details(property_details.to_dict())
            else:
                print("Property not found")
        except Exception as e:
            print(f"Error getting property details: {e}")
    else:
        print("Invalid choice")

def search_properties(zillow: ZillowService):
    """Search for properties using criteria."""
    print("\n=== Property Search ===")
    
    # Get location
    location = input("Enter location (e.g., 'San Francisco, CA'): ").strip()
    if not location:
        print("Error: Location cannot be empty")
        return
    
    # Get price range
    min_price = input("Enter minimum price (or press Enter to skip): ").strip()
    max_price = input("Enter maximum price (or press Enter to skip): ").strip()
    
    # Get bedrooms
    min_beds = input("Enter minimum bedrooms (or press Enter to skip): ").strip()
    max_beds = input("Enter maximum bedrooms (or press Enter to skip): ").strip()
    
    # Get bathrooms
    min_baths = input("Enter minimum bathrooms (or press Enter to skip): ").strip()
    max_baths = input("Enter maximum bathrooms (or press Enter to skip): ").strip()
    
    # Get property type
    print("\nProperty Types: Single Family, Condo, Townhouse, Multi Family, Lot/Land")
    property_type = input("Enter property type (or press Enter to skip): ").strip()
    
    # Create search criteria
    criteria = PropertySearchCriteria(
        location=location,
        min_price=float(min_price) if min_price else None,
        max_price=float(max_price) if max_price else None,
        min_beds=int(min_beds) if min_beds else None,
        max_beds=int(max_beds) if max_beds else None,
        min_baths=float(min_baths) if min_baths else None,
        max_baths=float(max_baths) if max_baths else None,
        property_type=property_type if property_type else None
    )
    
    try:
        print("\nSearching for properties...")
        properties = zillow.search_properties(criteria)
        
        if properties:
            print(f"\nFound {len(properties)} properties:")
            for i, prop in enumerate(properties, 1):
                print(f"\nProperty {i}:")
                format_property_details(prop.to_dict())
        else:
            print("No properties found matching your criteria")
    except Exception as e:
        print(f"Error searching for properties: {e}")

def get_rent_estimate(zillow: ZillowService):
    """Get rent estimate for a property."""
    print("\n=== Rent Estimate ===")
    
    # Get property details
    address = input("Enter property address: ").strip()
    if not address:
        print("Error: Address cannot be empty")
        return
    
    property_type = input("Enter property type (e.g., Single Family, Condo): ").strip()
    if not property_type:
        print("Error: Property type cannot be empty")
        return
    
    beds = input("Enter number of bedrooms: ").strip()
    try:
        beds = int(beds)
    except ValueError:
        print("Error: Invalid number of bedrooms")
        return
    
    baths = input("Enter number of bathrooms: ").strip()
    try:
        baths = float(baths)
    except ValueError:
        print("Error: Invalid number of bathrooms")
        return
    
    try:
        print("\nGetting rent estimate...")
        rent = zillow.get_rent_estimate(property_type, address, beds, baths)
        
        if rent:
            print(f"\nEstimated Monthly Rent: ${rent:,.2f}")
        else:
            print("Could not estimate rent for this property")
    except Exception as e:
        print(f"Error getting rent estimate: {e}")

def get_comparable_properties(zillow: ZillowService):
    """Get and display comparable properties based on user input."""
    print("\n=== Find Comparable Properties ===")
    print("Please enter the property address to find comparables:")
    address = input("Address: ").strip()
    
    if not address:
        print("Error: Address cannot be empty")
        return
    
    try:
        # First get the property details to get the zpid
        print(f"\nLooking up property: {address}")
        property_details = zillow.get_property_details(address)
        
        if not property_details:
            print("Property not found")
            return
        
        # Get radius from user
        radius = input("\nEnter search radius in miles (default: 1.0): ").strip()
        try:
            radius = float(radius) if radius else 1.0
        except ValueError:
            print("Invalid radius, using default of 1.0 miles")
            radius = 1.0
        
        # Get number of comparables from user
        limit = input("Enter number of comparable properties to show (default: 5): ").strip()
        try:
            limit = int(limit) if limit else 5
        except ValueError:
            print("Invalid number, using default of 5 properties")
            limit = 5
        
        print(f"\nFinding up to {limit} comparable properties within {radius} miles...")
        comps = zillow.get_comparable_properties(property_details.zpid, radius_miles=radius, limit=limit)
        
        if comps:
            print(f"\nFound {len(comps)} comparable properties:")
            for i, comp in enumerate(comps, 1):
                print(f"\nComparable Property {i}:")
                comp_dict = comp.to_dict()
                for key, value in comp_dict.items():
                    if value is not None and value != 0:  # Only show non-empty values
                        if isinstance(value, float):
                            if key in ['price', 'zestimate', 'rent_estimate', 'last_sold_price']:
                                print(f"{key.replace('_', ' ').title()}: ${value:,.2f}")
                            else:
                                print(f"{key.replace('_', ' ').title()}: {value}")
                        else:
                            print(f"{key.replace('_', ' ').title()}: {value}")
        else:
            print("No comparable properties found")
    except Exception as e:
        print(f"Error getting comparable properties: {e}")

def main():
    # Initialize the Zillow service
    zillow = ZillowService()
    
    while True:
        print("\n=== Zillow Property Tool ===")
        print("1. Look up property details")
        print("2. Search for properties")
        print("3. Get rent estimate")
        print("4. Find comparable properties")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            get_property_details(zillow)
        elif choice == "2":
            search_properties(zillow)
        elif choice == "3":
            get_rent_estimate(zillow)
        elif choice == "4":
            get_comparable_properties(zillow)
        elif choice == "5":
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")

if __name__ == "__main__":
    # Check for API key
    if not os.getenv("RAPIDAPI_ZILLOW_API_KEY"):
        print("Error: RAPIDAPI_ZILLOW_API_KEY environment variable not set")
        print("Please set your RapidAPI key for the Zillow API:")
        print('export RAPIDAPI_ZILLOW_API_KEY="your-api-key-here"')
    else:
        main()
