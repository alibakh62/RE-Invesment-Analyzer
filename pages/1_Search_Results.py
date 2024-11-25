"""Property search results and comparison page."""
import streamlit as st
import pandas as pd
from typing import List, Optional

from src.models.property import PropertyDetails
from src.services.zillow_service import ZillowService
from src.utils.data_prep import InvestmentAnalyzer, InvestmentAssumptions
from src.utils.visualizations import InvestmentVisualizer
from src.config.settings import DEFAULT_SEARCH_CRITERIA

def format_price(price: float) -> str:
    """Format price with commas and dollar sign."""
    return f"${price:,.0f}"

def display_property_card(
    property_details: PropertyDetails,
    analyzer: InvestmentAnalyzer,
    visualizer: InvestmentVisualizer
) -> None:
    """Display a property card with key information and metrics."""
    with st.container():
        col1, col2 = st.columns([2, 3])
        
        with col1:
            if property_details.image_urls:
                st.image(
                    property_details.image_urls[0],
                    caption=property_details.address,
                    use_column_width=True
                )
            
            st.markdown(f"""
            ### {property_details.address}
            **Price:** {format_price(property_details.price)}  
            **Beds:** {property_details.bedrooms} | **Baths:** {property_details.bathrooms}  
            **Sq.Ft:** {property_details.square_feet:,}
            """)
        
        with col2:
            # Quick analysis
            analysis = analyzer.analyze_property(property_details)
            if analysis:
                metrics = analysis['metrics']
                
                # Display key metrics
                cols = st.columns(2)
                cols[0].metric("Cap Rate", f"{metrics.cap_rate:.1f}%")
                cols[1].metric("Cash on Cash", f"{metrics.cash_on_cash:.1f}%")
                
                # Monthly financials
                st.markdown("### Monthly Financials")
                cols = st.columns(3)
                cols[0].metric("Rent", format_price(analysis['monthly_rent']))
                cols[1].metric("Mortgage", format_price(analysis['monthly_mortgage']))
                cols[2].metric(
                    "Net Cash Flow",
                    format_price(
                        analysis['monthly_rent'] - 
                        analysis['monthly_mortgage'] - 
                        analysis['operating_expenses']['Total_Expenses']/12
                    )
                )
                
                # Action buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Full Analysis", key=f"analyze_{property_details.zpid}"):
                        st.session_state['property_for_analysis'] = property_details
                        st.experimental_rerun()
                
                with col2:
                    if st.button("Compare", key=f"compare_{property_details.zpid}"):
                        if 'comparison_properties' not in st.session_state:
                            st.session_state['comparison_properties'] = []
                        if len(st.session_state['comparison_properties']) < 3:
                            st.session_state['comparison_properties'].append(property_details)
                            st.success("Added to comparison!")
                        else:
                            st.warning("Maximum 3 properties for comparison.")

def main():
    """Main function for search results page."""
    st.title("Search Results")
    
    # Initialize services if not in session state
    if 'zillow' not in st.session_state:
        st.session_state['zillow'] = ZillowService()
    if 'analyzer' not in st.session_state:
        st.session_state['analyzer'] = InvestmentAnalyzer(st.session_state['zillow'])
    if 'visualizer' not in st.session_state:
        st.session_state['visualizer'] = InvestmentVisualizer()
    
    # Get properties from session state
    properties = st.session_state.get('properties', [])
    
    if not properties:
        st.warning("No properties found. Please perform a search from the home page.")
        return
    
    # Filter options
    st.subheader("Filter Results")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_price = st.number_input(
            "Min Price",
            min_value=0,
            value=DEFAULT_SEARCH_CRITERIA['min_price'],
            step=50000
        )
        
        min_beds = st.number_input(
            "Min Beds",
            min_value=0,
            value=DEFAULT_SEARCH_CRITERIA['min_beds'],
            step=1
        )
    
    with col2:
        max_price = st.number_input(
            "Max Price",
            min_value=0,
            value=DEFAULT_SEARCH_CRITERIA['max_price'],
            step=50000
        )
        
        max_beds = st.number_input(
            "Max Beds",
            min_value=0,
            value=DEFAULT_SEARCH_CRITERIA['max_beds'],
            step=1
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort By",
            ["Price (Low to High)", "Price (High to Low)", "Beds", "Baths", "Square Feet"]
        )
    
    # Apply filters
    filtered_properties = [
        p for p in properties
        if min_price <= p.price <= max_price and
        min_beds <= p.bedrooms <= max_beds
    ]
    
    # Sort properties
    if sort_by == "Price (Low to High)":
        filtered_properties.sort(key=lambda x: x.price)
    elif sort_by == "Price (High to Low)":
        filtered_properties.sort(key=lambda x: x.price, reverse=True)
    elif sort_by == "Beds":
        filtered_properties.sort(key=lambda x: x.bedrooms, reverse=True)
    elif sort_by == "Baths":
        filtered_properties.sort(key=lambda x: x.bathrooms, reverse=True)
    elif sort_by == "Square Feet":
        filtered_properties.sort(key=lambda x: x.square_feet, reverse=True)
    
    # Display results count
    st.markdown(f"### Found {len(filtered_properties)} properties")
    
    # Property comparison section
    if 'comparison_properties' in st.session_state and st.session_state['comparison_properties']:
        with st.expander("Property Comparison", expanded=True):
            comparison_props = st.session_state['comparison_properties']
            
            # Create comparison table
            comparison_data = []
            for prop in comparison_props:
                analysis = st.session_state['analyzer'].analyze_property(prop)
                if analysis:
                    metrics = analysis['metrics']
                    comparison_data.append({
                        'Address': prop.address,
                        'Price': format_price(prop.price),
                        'Monthly Rent': format_price(analysis['monthly_rent']),
                        'Cap Rate': f"{metrics.cap_rate:.1f}%",
                        'Cash on Cash': f"{metrics.cash_on_cash:.1f}%",
                        'IRR': f"{metrics.irr:.1f}%"
                    })
            
            if comparison_data:
                df = pd.DataFrame(comparison_data)
                st.table(df)
                
                if st.button("Clear Comparison"):
                    st.session_state['comparison_properties'] = []
                    st.experimental_rerun()
    
    # Display property cards
    for property_details in filtered_properties:
        display_property_card(
            property_details,
            st.session_state['analyzer'],
            st.session_state['visualizer']
        )
        st.markdown("---")

if __name__ == "__main__":
    main()
