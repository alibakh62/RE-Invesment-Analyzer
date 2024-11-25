"""Application configuration and settings."""
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Data directory for storing temporary files
DATA_DIR = BASE_DIR / 'data'
if not DATA_DIR.exists():
    DATA_DIR.mkdir(parents=True)

# API Configuration
API_CONFIG = {
    'ZILLOW_API_KEY': os.getenv('RAPIDAPI_ZILLOW_API_KEY'),
    'ZILLOW_API_HOST': 'zillow-com1.p.rapidapi.com',
    'ZILLOW_BASE_URL': 'https://zillow-com1.p.rapidapi.com'
}

# Default investment assumptions
DEFAULT_INVESTMENT_ASSUMPTIONS = {
    'equity_percentage': 20.0,
    'interest_rate': 7.0,
    'amortization_period': 30,
    'renovation_budget': 0.0,
    'extra_cash_reserves': 0.0,
    'rental_growth_rate': 2.0,
    'expense_growth_rate': 2.0,
    'vacancy_rate': 5.0,
    'property_mgmt_rate': 10.0,
    'maintenance_rate': 5.0,
}

# Property search defaults
DEFAULT_SEARCH_CRITERIA = {
    'status_type': 'ForSale',
    'sort_by': 'Price_Low_High',
    'min_price': 100000,
    'max_price': 1000000,
    'min_beds': 2,
    'max_beds': 4,
    'min_baths': 1,
    'max_baths': 3,
    'min_sqft': 1000,
    'max_sqft': 3000,
}

# Valid property types
PROPERTY_TYPES = [
    'SingleFamily',
    'Condo',
    'Townhouse',
    'MultiFamily',
    'Apartment',
    'Duplex',
    'Triplex',
    'Quadruplex'
]

# Analysis settings
ANALYSIS_CONFIG = {
    'default_holding_period': 5,
    'min_holding_period': 1,
    'max_holding_period': 30,
    'default_appreciation_rate': 3.0,
    'closing_cost_rate': 2.0,
    'property_tax_rate': 1.2,
    'insurance_rate': 0.5,
}

# Cache settings
CACHE_CONFIG = {
    'CACHE_DIR': DATA_DIR / 'cache',
    'MAX_AGE': 3600,  # Cache expiration in seconds
    'PROPERTY_CACHE_SIZE': 1000,  # Number of properties to cache
    'SEARCH_CACHE_SIZE': 100,  # Number of search results to cache
}

# Create cache directory if it doesn't exist
if not CACHE_CONFIG['CACHE_DIR'].exists():
    CACHE_CONFIG['CACHE_DIR'].mkdir(parents=True)

# Streamlit configuration
STREAMLIT_CONFIG = {
    'PAGE_TITLE': 'Real Estate Investment Analyzer',
    'PAGE_ICON': '🏠',
    'LAYOUT': 'wide',
    'MENU_ITEMS': {
        'About': 'Real Estate Investment Analysis Tool',
        'Report a Bug': 'https://github.com/yourusername/real-estate-analyzer/issues',
        'Get Help': 'https://github.com/yourusername/real-estate-analyzer/wiki'
    }
}
