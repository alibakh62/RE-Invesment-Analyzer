"""Detailed property analysis page."""
import streamlit as st
import pandas as pd
from typing import Dict, Any

from src.models.property import PropertyDetails
from src.services.zillow_service import ZillowService
from src.utils.data_prep import InvestmentAnalyzer, InvestmentAssumptions
from src.utils.visualizations import InvestmentVisualizer
from src.config.settings import ANALYSIS_CONFIG

def format_currency(value: float) -> str:
    """Format currency with dollar sign and commas."""
    return f"${value:,.2f}"

def display_property_header(property_details: PropertyDetails) -> None:
    """Display property header with basic information."""
    col1, col2 = st.columns([2, 3])
    
    with col1:
        if property_details.image_urls:
            st.image(
                property_details.image_urls[0],
                caption="Primary Image",
                use_column_width=True
            )
    
    with col2:
        st.title(property_details.address)
        st.markdown(f"""
        ### Property Details
        - **Price:** {format_currency(property_details.price)}
        - **Bedrooms:** {property_details.bedrooms}
        - **Bathrooms:** {property_details.bathrooms}
        - **Square Feet:** {property_details.square_feet:,}
        - **Year Built:** {property_details.year_built}
        - **Property Type:** {property_details.property_type}
        """)

def display_investment_assumptions(
    assumptions: InvestmentAssumptions,
    on_change: callable
) -> None:
    """Display and edit investment assumptions."""
    with st.expander("Investment Assumptions", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            assumptions.equity_percentage = st.number_input(
                "Down Payment (%)",
                min_value=0.0,
                max_value=100.0,
                value=assumptions.equity_percentage,
                step=5.0,
                on_change=on_change
            )
            
            assumptions.interest_rate = st.number_input(
                "Interest Rate (%)",
                min_value=0.0,
                max_value=20.0,
                value=assumptions.interest_rate,
                step=0.25,
                on_change=on_change
            )
            
            assumptions.amortization_period = st.number_input(
                "Amortization Period (years)",
                min_value=1,
                max_value=30,
                value=assumptions.amortization_period,
                step=1,
                on_change=on_change
            )
        
        with col2:
            assumptions.vacancy_rate = st.number_input(
                "Vacancy Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=assumptions.vacancy_rate,
                step=1.0,
                on_change=on_change
            )
            
            assumptions.maintenance_rate = st.number_input(
                "Maintenance Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=assumptions.maintenance_rate,
                step=1.0,
                on_change=on_change
            )
            
            assumptions.property_mgmt_rate = st.number_input(
                "Property Management (%)",
                min_value=0.0,
                max_value=100.0,
                value=assumptions.property_mgmt_rate,
                step=1.0,
                on_change=on_change
            )
        
        with col3:
            assumptions.appreciation_rate = st.number_input(
                "Appreciation Rate (%)",
                min_value=0.0,
                max_value=20.0,
                value=assumptions.appreciation_rate,
                step=0.5,
                on_change=on_change
            )
            
            assumptions.rental_growth_rate = st.number_input(
                "Rental Growth Rate (%)",
                min_value=0.0,
                max_value=20.0,
                value=assumptions.rental_growth_rate,
                step=0.5,
                on_change=on_change
            )
            
            assumptions.holding_period = st.number_input(
                "Holding Period (years)",
                min_value=1,
                max_value=30,
                value=assumptions.holding_period,
                step=1,
                on_change=on_change
            )

def display_analysis_results(
    analysis: Dict[str, Any],
    visualizer: InvestmentVisualizer
) -> None:
    """Display analysis results with visualizations."""
    # Key Metrics
    st.header("Investment Analysis")
    metrics = analysis['metrics']
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("IRR", f"{metrics.irr:.1f}%")
    col2.metric("Cap Rate", f"{metrics.cap_rate:.1f}%")
    col3.metric("Cash on Cash", f"{metrics.cash_on_cash:.1f}%")
    col4.metric("ROI", f"{metrics.roi:.1f}%")
    
    # Monthly Financials
    st.subheader("Monthly Financials")
    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Rental Income",
        format_currency(analysis['monthly_rent'])
    )
    col2.metric(
        "Operating Expenses",
        format_currency(analysis['operating_expenses']['Total_Expenses']/12)
    )
    col3.metric(
        "Mortgage Payment",
        format_currency(analysis['monthly_mortgage'])
    )
    
    # Operating Expenses Breakdown
    st.subheader("Operating Expenses Breakdown")
    st.plotly_chart(
        visualizer.plot_operating_expenses(analysis['operating_expenses']),
        use_container_width=True
    )
    
    # Cash Flow Analysis
    st.subheader("Cash Flow Analysis")
    st.plotly_chart(
        visualizer.plot_cash_flows(analysis['cash_flows']),
        use_container_width=True
    )
    
    # Investment Metrics Radar
    st.subheader("Investment Metrics Overview")
    st.plotly_chart(
        visualizer.plot_metrics_radar(metrics.__dict__),
        use_container_width=True
    )
    
    # Amortization Schedule
    st.subheader("Loan Amortization")
    st.plotly_chart(
        visualizer.plot_amortization(analysis['amortization']),
        use_container_width=True
    )
    
    # Detailed Cash Flow Table
    st.subheader("Detailed Cash Flow Projections")
    st.dataframe(
        analysis['cash_flows'].style.format({
            col: "${:,.2f}" for col in analysis['cash_flows'].select_dtypes('float64').columns
        })
    )

def main():
    """Main function for property analysis page."""
    if 'property_for_analysis' not in st.session_state:
        st.warning("No property selected for analysis. Please select a property from the search results.")
        return
    
    # Initialize services if not in session state
    if 'zillow' not in st.session_state:
        st.session_state['zillow'] = ZillowService()
    if 'analyzer' not in st.session_state:
        st.session_state['analyzer'] = InvestmentAnalyzer(st.session_state['zillow'])
    if 'visualizer' not in st.session_state:
        st.session_state['visualizer'] = InvestmentVisualizer()
    
    property_details = st.session_state['property_for_analysis']
    
    # Display property header
    display_property_header(property_details)
    
    # Get or create assumptions
    if 'current_assumptions' not in st.session_state:
        st.session_state['current_assumptions'] = InvestmentAssumptions()
    
    # Display assumptions with callback
    def update_analysis():
        """Callback for assumption changes."""
        st.session_state['current_analysis'] = st.session_state['analyzer'].analyze_property(
            property_details
        )
    
    display_investment_assumptions(
        st.session_state['current_assumptions'],
        update_analysis
    )
    
    # Perform analysis if needed
    if 'current_analysis' not in st.session_state:
        with st.spinner("Analyzing property..."):
            st.session_state['current_analysis'] = st.session_state['analyzer'].analyze_property(
                property_details
            )
    
    # Display results
    if st.session_state['current_analysis']:
        display_analysis_results(
            st.session_state['current_analysis'],
            st.session_state['visualizer']
        )
        
        # Save to recent analyses
        if 'recent_analyses' not in st.session_state:
            st.session_state['recent_analyses'] = {}
        st.session_state['recent_analyses'][property_details.address] = st.session_state['current_analysis']
    else:
        st.error("Failed to analyze property. Please check your assumptions and try again.")

if __name__ == "__main__":
    main()
