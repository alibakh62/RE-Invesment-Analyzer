"""Data formatting utilities."""
from typing import Any, Dict, List, Union
import pandas as pd
import numpy as np

def format_currency(value: float, include_cents: bool = False) -> str:
    """Format number as currency."""
    if pd.isna(value) or value is None:
        return '$0'
    
    if include_cents:
        return f"${value:,.2f}"
    return f"${int(value):,}"

def format_percentage(value: float, decimals: int = 2) -> str:
    """Format number as percentage."""
    if pd.isna(value) or value is None:
        return '0%'
    
    return f"{value:.{decimals}f}%"

def format_number(value: float, decimals: int = 0) -> str:
    """Format number with thousand separators."""
    if pd.isna(value) or value is None:
        return '0'
    
    return f"{value:,.{decimals}f}"

def format_metrics_table(metrics: Dict[str, float]) -> pd.DataFrame:
    """Format investment metrics for display."""
    formatted_metrics = {}
    
    # Format different metric types appropriately
    for key, value in metrics.items():
        if 'price' in key.lower() or 'value' in key.lower() or 'cash' in key.lower():
            formatted_metrics[key] = format_currency(value)
        elif 'rate' in key.lower() or 'roi' in key.lower() or 'irr' in key.lower():
            formatted_metrics[key] = format_percentage(value)
        else:
            formatted_metrics[key] = format_number(value)
    
    return pd.DataFrame(formatted_metrics.items(), columns=['Metric', 'Value'])

def format_cash_flow_table(cash_flows: pd.DataFrame) -> pd.DataFrame:
    """Format cash flow projections for display."""
    formatted_df = cash_flows.copy()
    
    # Format currency columns
    currency_columns = ['Cash Flow', 'Operating Income', 'Operating Expenses']
    for col in currency_columns:
        if col in formatted_df.columns:
            formatted_df[col] = formatted_df[col].apply(format_currency)
    
    # Format percentage columns
    pct_columns = ['Growth Rate', 'Yield']
    for col in pct_columns:
        if col in formatted_df.columns:
            formatted_df[col] = formatted_df[col].apply(format_percentage)
    
    return formatted_df

def format_property_details(property_data: Dict[str, Any]) -> Dict[str, str]:
    """Format property details for display."""
    formatted = {}
    
    # Format different property attributes appropriately
    formatters = {
        'price': lambda x: format_currency(float(x)),
        'zestimate': lambda x: format_currency(float(x)),
        'rent_estimate': lambda x: format_currency(float(x)),
        'last_sold_price': lambda x: format_currency(float(x)),
        'square_feet': lambda x: f"{format_number(float(x))} sq ft",
        'lot_size': lambda x: f"{format_number(float(x))} sq ft",
        'year_built': lambda x: str(x),
        'days_on_zillow': lambda x: f"{x} days",
        'bedrooms': lambda x: f"{x} beds",
        'bathrooms': lambda x: f"{x} baths"
    }
    
    for key, value in property_data.items():
        if value is None or pd.isna(value):
            formatted[key] = 'N/A'
        elif key in formatters:
            try:
                formatted[key] = formatters[key](value)
            except (ValueError, TypeError):
                formatted[key] = str(value)
        else:
            formatted[key] = str(value)
    
    return formatted

def format_amortization_table(schedule: pd.DataFrame) -> pd.DataFrame:
    """Format amortization schedule for display."""
    formatted_df = schedule.copy()
    
    # Format currency columns
    currency_columns = ['Payment', 'Principal', 'Interest', 'Balance']
    for col in currency_columns:
        formatted_df[col] = formatted_df[col].apply(lambda x: format_currency(x, include_cents=True))
    
    # Format period as integer
    formatted_df['Period'] = formatted_df['Period'].astype(int)
    
    return formatted_df
