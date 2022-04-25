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

def app():
    """
    In this page, user can see the default assumptions for the project.
    """
    st.markdown("<h1 style='text-align: center; color: black;'>Default Investment Assumptions</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: grey;'>You can change any of assumptions. Hit the Submit button to save the defaults.</p>", unsafe_allow_html=True)

    with st.container():
        c1, c2, c3 = st.columns([2,1,2])
        c1.markdown("<h3 style='text-align: center; color: black;'>Financing</h3>", unsafe_allow_html=True)
        # c2.markdown("<h3 style='text-align: center; color: black;'>Renovation Assumptions</h3>", unsafe_allow_html=True)
        c3.markdown("<h3 style='text-align: center; color: black;'>Renovation Costs</h3>", unsafe_allow_html=True)
        with c1:
            with st.form("Financing"):
                extra_cash_reserves = st.number_input("Extra Cash Reserves", value=2500, step=1_000, help="Typically 1-2% of purchase price")
                eqt_pct = st.number_input("Equity % of Total Project Cost", value=0.5)
                amort_period = st.number_input("Amortization Period (years)", value=30, step=1)
                int_rate_on_debt = st.number_input("Interest Rate (%) on Debt", value=0.05)
                submitted_financing = st.form_submit_button("Submit")
                if submitted_financing:
                    user_assumptions['extra_cash_reserves'] = extra_cash_reserves
                    user_assumptions['eqt_pct'] = eqt_pct
                    user_assumptions['amort_period'] = amort_period
                    user_assumptions['int_rate_on_debt'] = int_rate_on_debt
                    # with open('data/user_assumptions_test.json', 'w') as f:
                    #     json.dump(user_assumptions, f)
                    # st.success("Financing Assumptions Updated")
        with c2:
            st.write('')
        with c3:
            with st.form("Renovation Costs"):
                renovation_costs = st.number_input("Renovation Costs", value=10_000, step=1_000)
                renovation_period = st.number_input("Renovation Period (months)", value=4, step=1)
                exit_renovation_cost = st.number_input("Exit Renovation Costs", value=5_000, step=1_000)
                submitted_renov = st.form_submit_button("Submit")
                if submitted_renov:
                    user_assumptions['renovation_costs'] = renovation_costs
                    user_assumptions['renovation_period'] = renovation_period
                    user_assumptions['exit_renovation_cost'] = exit_renovation_cost
                    # with open('data/user_assumptions_test.json', 'w') as f:
                    #     json.dump(user_assumptions, f)
                    # st.success("Renovation Assumptions Updated")
        
    with st.container():
        c1, c2, c3 = st.columns([2,1,2])
        c1.markdown("<h3 style='text-align: center; color: black;'>Exit</h3>", unsafe_allow_html=True)
        # c2.markdown("<h3 style='text-align: center; color: black;'>Rental Growth</h3>", unsafe_allow_html=True)
        c3.markdown("<h3 style='text-align: center; color: black;'>Other</h3>", unsafe_allow_html=True)
        with c1:
            with st.form("Exit"):
                length_hold = st.number_input("Length of Hold (years)", value=7, step=1)
                appr_rate = st.number_input("Appreciation Rate (%/year)", value=0.05)
                # sales_price_at_exit = st.number_input("Sales Price at Exit ($)", value=int(default_values["sales_price_at_exit"]), step=1_000)
                cost_of_sale = st.number_input("Cost of Sale (%)", value=0.06, help="Cost of Sale includes broker fee and closing costs as a percentage of sales price")
                submitted_exit = st.form_submit_button("Submit")
                if submitted_exit:
                    user_assumptions['length_hold'] = length_hold
                    user_assumptions['appr_rate'] = appr_rate
                    # user_assumptions['sales_price_at_exit'] = sales_price_at_exit
                    user_assumptions['cost_of_sale'] = cost_of_sale
                    # with open('data/user_assumptions_test.json', 'w') as f:
                    #     json.dump(user_assumptions, f)
                    # st.success("Exit Assumptions Updated")
        with c2:
            st.write('')
        with c3:
            with st.form("Others"):
                vacancy_rate = st.number_input("Vacancy Rate (%/year)", value=0.0775, help="Vacancy rate is the percentage of the year that the property is vacant")
                rent_growth_rate = st.number_input("Rent Growth Rate (%/year)", value=0.02, help="Rent growth rate is the percentage increase in rent per year")
                repairs = st.number_input("Repairs (%/monthly)", value=0.07, help="Repairs and maintenance costs as a percentage of monthly rent")
                property_taxes = st.number_input("Property Taxes ($/year)", value=1_000, step=100)
                insurance = st.number_input("Insurance ($/year)", value=1_000, step=100)
                utilities = st.number_input("Utilities ($/month)", value=100, step=10)
                property_manager_fee = st.number_input("Property Manager Fee (%/month)", value=0.02, help="Property Manager Fee is the percentage of monthly rent charged to the property manager")
                discount_rate = st.number_input("Discount Rate (%)", value=0.05, help="Discount rate for calculating the NPV")
                submitted_others = st.form_submit_button("Submit")
                if submitted_others:
                    user_assumptions['vacancy_rate'] = vacancy_rate
                    user_assumptions['rent_growth_rate'] = rent_growth_rate
                    user_assumptions['repairs'] = repairs
                    user_assumptions['property_taxes'] = property_taxes
                    user_assumptions['insurance'] = insurance
                    user_assumptions['utilities'] = utilities
                    user_assumptions['property_manager_fee'] = property_manager_fee
                    user_assumptions['discount_rate'] = discount_rate
                    # with open('data/user_assumptions_test.json', 'w') as f:
                    #     json.dump(user_assumptions, f)
                    # st.success("Other Assumptions Updated")