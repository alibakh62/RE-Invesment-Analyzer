import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import sys
sys.path.insert(0, '.')
sys.path.insert(0, '..')

with open('data/user_assumptions_test.json', 'r') as f:
    user_assumptions = json.load(f)

core_assumptions = {
    "Monthly Gross Rent ($/mo)": user_assumptions["monthly_gross_rent"],
    "Purchase Price ($)": user_assumptions["purchase_price"],
    # "Purchase Date": datetime.strptime(user_assumptions["purchase_date"], '%Y-%m-%d'),  #TODO: handle this
    "Closing Costs ($)": user_assumptions["closing_costs"],
    "Extra Cash Reserves ($)": user_assumptions["extra_cash_reserves"],
}

renovations = {
    "Initial Renovation Cost ($)": user_assumptions["renovation_costs"],
    "Renovation Period (months)": user_assumptions["renovation_period"],
    "Exit Renovation Cost ($)": user_assumptions["exit_renovation_cost"],
    "Total Project Cost ($)": user_assumptions["purchase_price"] + user_assumptions["closing_costs"] + user_assumptions["renovation_period"] + user_assumptions["exit_renovation_cost"], 
}

financial_assumptions = {
    "Equity % of Total Project Cost": user_assumptions['eqt_pct'],
    "Total Project Loan Amount ($)": np.round((1 - user_assumptions['eqt_pct'])*(user_assumptions["purchase_price"] + user_assumptions["closing_costs"] + user_assumptions["renovation_period"] + user_assumptions["exit_renovation_cost"]), 0),  # calculated
    "Amortization Period (years)": user_assumptions['amort_period'],
    "Interest Rate (%) on Debt": user_assumptions['int_rate_on_debt'],
}

exit_assumptions = {
    "Length of Hold (years)": user_assumptions['length_hold'],
    "Appreciation Rate (%/year)": user_assumptions['appr_rate'],
    "Sales Price at Exit ($)": user_assumptions['sales_price_at_exit'],  # calculated
    "Cost of Sale (%)": user_assumptions['cost_of_sale'],
}

other_assumptions = {
    "Vacancy Rate (%/year)": user_assumptions['vacancy_rate'],
    "Rent Growth Rate (%/year)": user_assumptions['rent_growth_rate'],
    "Repairs and Maintenance (%/month)": user_assumptions['repairs'],
    "Property Taxes ($/year)": user_assumptions['property_taxes'],
    "Insurance ($/year)": user_assumptions['insurance'],
    "Utilities ($/month)": user_assumptions['utilities'],
    "Property Management Fees (%/month)": user_assumptions['property_manager_fee'],
    "Discount Rate (%)": user_assumptions['discount_rate'],
}

def app():
    """
    This is the main analysis page.
    """
    st.markdown("<h1 style='text-align: center; color: black;'>Assumption Review</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: grey;'>Review the assumptions below and click the 'Submit' button to continue.</p>", unsafe_allow_html=True)
    # st.title("Review Your Assumptions")
    # st.write("Review the assumptions below and click the 'Submit' button to continue.")
    # col1, col2, col3, col4, col5 = st.columns(5)

    with st.container():
        col1, col2, col3 = st.columns([2,1,2])
        with col1:
            st.subheader("Core Deal Assumptions")
            st.dataframe(pd.DataFrame.from_dict(core_assumptions, orient='index'))

        with col2:
            st.write('')

        with col3:
            st.subheader("Renovations")
            st.dataframe(pd.DataFrame.from_dict(renovations, orient='index'))

    with st.container():
        col4, col5, col6 = st.columns([2,1,2])
        with col4:
            st.subheader("Financing Related")
            st.table(pd.DataFrame.from_dict(financial_assumptions, orient='index'))
        
        with col5:
            st.write('')

        with col6:
            st.subheader("Exit Assumptions")
            st.table(pd.DataFrame.from_dict(exit_assumptions, orient='index'))

        with st.container():
            col7, col8, col9 = st.columns([1,2,1])	
            with col7:
                st.write('')
            with col8:
                st.subheader("Other Assumptions")
                st.table(pd.DataFrame.from_dict(other_assumptions, orient='index'))
            with col9:
                st.write('')

    with st.container():
        col10, col11, col12 = st.columns(3)	
        with col10:
            st.write('')
        with col11:
            form = st.form("Submit Assumptions")
            # m = st.markdown("""
            # <style>
            # div.stButton > button:first-child {
            #     background-color: rgb(204, 49, 49);
            # }
            # </style>""", unsafe_allow_html=True)
            rejected = form.form_submit_button("Edit")
            confirmed = form.form_submit_button("Confirm Assumptions")
            if confirmed:
                st.write("Assumptions confirmed.")
                st.write("You can now continue to the property analysis page.")
                st.balloons()
                st.markdown("<a href='/Analysis'>Click here to continue.</a>", unsafe_allow_html=True)
            if rejected:
                st.write("Please return to the assumptions page and make changes and submit again.")
        with col12:
            st.write('')
