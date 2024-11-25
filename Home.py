"""Real Estate Investment Analyzer main app."""
import streamlit as st
from pathlib import Path
import os

from src.config.settings import STREAMLIT_CONFIG
from src.services.zillow_service import ZillowService
from src.utils.data_prep import InvestmentAnalyzer, InvestmentAssumptions
from src.utils.validators import validate_numeric, validate_percentage
from src.utils.visualizations import InvestmentVisualizer

# Configure Streamlit page
st.set_page_config(
    page_title=STREAMLIT_CONFIG['PAGE_TITLE'],
    page_icon=STREAMLIT_CONFIG['PAGE_ICON'],
    layout=STREAMLIT_CONFIG['LAYOUT']
)

def main():
    """Main app function."""
    # Initialize services
    zillow = ZillowService()
    analyzer = InvestmentAnalyzer(zillow)
    visualizer = InvestmentVisualizer()
    
    # Header
    st.title("Real Estate Investment Analyzer")
    st.markdown("""
    Welcome to the Real Estate Investment Analyzer! This tool helps you:
    - Search for properties based on your criteria
    - Analyze potential investments
    - Compare multiple properties
    - Make data-driven investment decisions
    """)
    
    # Quick Search
    st.subheader("Quick Property Search")
    col1, col2 = st.columns(2)
    
    with col1:
        search_type = st.radio(
            "Search by:",
            ["Address", "MLS Number", "Zip Code"]
        )
        
        search_input = st.text_input(
            f"Enter {search_type.lower()}:",
            help=f"Enter a {search_type.lower()} to search for properties"
        )
    
    with col2:
        st.markdown("### Investment Criteria")
        min_price = st.number_input(
            "Minimum Price ($)",
            min_value=0,
            value=100000,
            step=50000
        )
        
        max_price = st.number_input(
            "Maximum Price ($)",
            min_value=0,
            value=1000000,
            step=50000
        )
    
    if st.button("Search Properties"):
        if search_input:
            with st.spinner("Searching properties..."):
                if search_type == "MLS Number":
                    property_result = zillow.search_by_mls(search_input)
                    if property_result:
                        st.session_state['property'] = property_result
                        st.experimental_rerun()
                else:
                    # Create search criteria
                    criteria = {
                        'location': search_input,
                        'min_price': min_price,
                        'max_price': max_price
                    }
                    properties = zillow.search_properties(criteria)
                    
                    if properties:
                        st.session_state['properties'] = properties
                        st.experimental_rerun()
                    else:
                        st.error("No properties found matching your criteria.")
        else:
            st.warning(f"Please enter a {search_type.lower()} to search.")
    
    # Investment Assumptions
    st.subheader("Default Investment Assumptions")
    with st.expander("View/Edit Assumptions"):
        col1, col2 = st.columns(2)
        
        with col1:
            equity_pct = st.number_input(
                "Down Payment (%)",
                min_value=0.0,
                max_value=100.0,
                value=20.0,
                step=5.0
            )
            
            interest_rate = st.number_input(
                "Interest Rate (%)",
                min_value=0.0,
                max_value=20.0,
                value=7.0,
                step=0.25
            )
            
            amort_period = st.number_input(
                "Amortization Period (years)",
                min_value=1,
                max_value=30,
                value=30,
                step=1
            )
        
        with col2:
            vacancy_rate = st.number_input(
                "Vacancy Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=5.0,
                step=1.0
            )
            
            maintenance_rate = st.number_input(
                "Maintenance Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=5.0,
                step=1.0
            )
            
            appreciation_rate = st.number_input(
                "Appreciation Rate (%)",
                min_value=0.0,
                max_value=20.0,
                value=3.0,
                step=0.5
            )
    
    # Save assumptions to session state
    if st.button("Save Assumptions"):
        assumptions = InvestmentAssumptions(
            equity_percentage=equity_pct,
            interest_rate=interest_rate,
            amortization_period=amort_period,
            vacancy_rate=vacancy_rate,
            maintenance_rate=maintenance_rate,
            appreciation_rate=appreciation_rate
        )
        st.session_state['assumptions'] = assumptions
        st.success("Investment assumptions saved!")
    
    # Recent Analyses
    if 'recent_analyses' in st.session_state:
        st.subheader("Recent Analyses")
        for address, analysis in st.session_state['recent_analyses'].items():
            with st.expander(f"Analysis for {address}"):
                # Display key metrics
                metrics = analysis['metrics']
                cols = st.columns(4)
                
                cols[0].metric(
                    "IRR",
                    f"{metrics.irr:.1f}%"
                )
                cols[1].metric(
                    "Cap Rate",
                    f"{metrics.cap_rate:.1f}%"
                )
                cols[2].metric(
                    "Cash on Cash",
                    f"{metrics.cash_on_cash:.1f}%"
                )
                cols[3].metric(
                    "ROI",
                    f"{metrics.roi:.1f}%"
                )
                
                # Plot cash flows
                st.plotly_chart(
                    visualizer.plot_cash_flows(analysis['cash_flows']),
                    use_container_width=True
                )

if __name__ == "__main__":
    main()
