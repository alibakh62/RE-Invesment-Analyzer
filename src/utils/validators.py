"""Input validation utilities."""
from typing import Any, Dict, Optional, Union, List
import re
from datetime import datetime

def validate_numeric(value: Any, min_value: float = None, max_value: float = None) -> Optional[float]:
    """Validate numeric input."""
    try:
        num = float(value)
        if min_value is not None and num < min_value:
            return None
        if max_value is not None and num > max_value:
            return None
        return num
    except (ValueError, TypeError):
        return None

def validate_percentage(value: Any) -> Optional[float]:
    """Validate percentage input (0-100)."""
    return validate_numeric(value, 0, 100)

def validate_year(value: Any) -> Optional[int]:
    """Validate year input."""
    try:
        year = int(value)
        if 1800 <= year <= 2100:  # Reasonable range for property years
            return year
        return None
    except (ValueError, TypeError):
        return None

def validate_address(address: str) -> bool:
    """Validate address format."""
    # Basic address validation
    if not address or len(address.strip()) < 5:
        return False
    
    # Check for common address components
    address_pattern = r'^[0-9]+\s+[A-Za-z0-9\s\.,#-]+$'
    return bool(re.match(address_pattern, address))

def validate_property_type(prop_type: str) -> Optional[str]:
    """Validate property type."""
    valid_types = {
        'SingleFamily', 'Condo', 'Townhouse', 'MultiFamily',
        'Apartment', 'Duplex', 'Triplex', 'Quadruplex'
    }
    
    return prop_type if prop_type in valid_types else None

def validate_search_criteria(criteria: Dict[str, Any]) -> Dict[str, str]:
    """Validate property search criteria."""
    errors = {}
    
    # Required fields
    required_fields = ['location']
    for field in required_fields:
        if field not in criteria or not criteria[field]:
            errors[field] = f"{field} is required"
    
    # Price range
    min_price = validate_numeric(criteria.get('min_price', 0))
    max_price = validate_numeric(criteria.get('max_price'))
    if min_price is not None and max_price is not None and min_price > max_price:
        errors['price_range'] = "Minimum price cannot be greater than maximum price"
    
    # Bedrooms
    min_beds = validate_numeric(criteria.get('min_beds', 0))
    max_beds = validate_numeric(criteria.get('max_beds'))
    if min_beds is not None and max_beds is not None and min_beds > max_beds:
        errors['beds_range'] = "Minimum beds cannot be greater than maximum beds"
    
    # Square footage
    min_sqft = validate_numeric(criteria.get('min_sqft', 0))
    max_sqft = validate_numeric(criteria.get('max_sqft'))
    if min_sqft is not None and max_sqft is not None and min_sqft > max_sqft:
        errors['sqft_range'] = "Minimum square footage cannot be greater than maximum"
    
    return errors

def validate_investment_assumptions(assumptions: Dict[str, Any]) -> Dict[str, str]:
    """Validate investment assumptions."""
    errors = {}
    
    # Validate equity percentage
    equity_pct = validate_percentage(assumptions.get('equity_percentage'))
    if equity_pct is None:
        errors['equity_percentage'] = "Equity percentage must be between 0 and 100"
    
    # Validate interest rate
    interest_rate = validate_percentage(assumptions.get('interest_rate'))
    if interest_rate is None:
        errors['interest_rate'] = "Interest rate must be between 0 and 100"
    
    # Validate amortization period
    amort_period = validate_numeric(assumptions.get('amortization_period'), 1, 40)
    if amort_period is None:
        errors['amortization_period'] = "Amortization period must be between 1 and 40 years"
    
    # Validate rates
    for rate_field in ['vacancy_rate', 'maintenance_rate', 'property_mgmt_rate']:
        rate = validate_percentage(assumptions.get(rate_field))
        if rate is None:
            errors[rate_field] = f"{rate_field.replace('_', ' ').title()} must be between 0 and 100"
    
    # Validate growth rates
    for growth_field in ['appreciation_rate', 'rental_growth_rate', 'expense_growth_rate']:
        rate = validate_percentage(assumptions.get(growth_field))
        if rate is None:
            errors[growth_field] = f"{growth_field.replace('_', ' ').title()} must be between 0 and 100"
    
    return errors

def validate_mls_number(mls: str) -> bool:
    """Validate MLS number format."""
    # Basic MLS validation - adjust pattern based on your region's format
    mls_pattern = r'^[A-Z0-9]{5,12}$'
    return bool(re.match(mls_pattern, mls.upper()))

def validate_zip_code(zip_code: str) -> bool:
    """Validate US zip code format."""
    zip_pattern = r'^\d{5}(?:-\d{4})?$'
    return bool(re.match(zip_pattern, zip_code))

def validate_phone(phone: str) -> bool:
    """Validate US phone number format."""
    phone_pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(phone_pattern, phone))

def validate_email(email: str) -> bool:
    """Validate email format."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

def validate_date(date_str: str, format: str = '%Y-%m-%d') -> Optional[datetime]:
    """Validate date string format."""
    try:
        return datetime.strptime(date_str, format)
    except ValueError:
        return None

def validate_currency(value: str) -> Optional[float]:
    """Validate currency format and convert to float."""
    try:
        # Remove currency symbol and commas
        cleaned = re.sub(r'[^\d.-]', '', value)
        return float(cleaned)
    except ValueError:
        return None

def validate_square_feet(value: Any) -> Optional[int]:
    """Validate square footage input."""
    try:
        sqft = int(float(value))  # Convert to float first to handle decimal inputs
        if 100 <= sqft <= 100000:  # Reasonable range for residential properties
            return sqft
        return None
    except (ValueError, TypeError):
        return None

def validate_property_details(details: Dict[str, Any]) -> Dict[str, str]:
    """Validate property details."""
    errors = {}
    
    # Required fields
    required_fields = ['address', 'price', 'square_feet']
    for field in required_fields:
        if field not in details or not details[field]:
            errors[field] = f"{field} is required"
    
    # Validate address
    if 'address' in details and not validate_address(details['address']):
        errors['address'] = "Invalid address format"
    
    # Validate price
    if 'price' in details:
        price = validate_currency(str(details['price']))
        if price is None or price <= 0:
            errors['price'] = "Invalid price"
    
    # Validate square footage
    if 'square_feet' in details:
        sqft = validate_square_feet(details['square_feet'])
        if sqft is None:
            errors['square_feet'] = "Invalid square footage"
    
    # Validate property type
    if 'property_type' in details:
        prop_type = validate_property_type(details['property_type'])
        if prop_type is None:
            errors['property_type'] = "Invalid property type"
    
    # Validate year built
    if 'year_built' in details:
        year = validate_year(details['year_built'])
        if year is None:
            errors['year_built'] = "Invalid year built"
    
    return errors
