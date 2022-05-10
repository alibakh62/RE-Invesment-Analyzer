import streamlit as st
import json
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.express as px
import pickle
from src.utils import DataPrep, InvestmentAssumptions
from src.metrics import Metrics
import sys
sys.path.insert(0, '.')
sys.path.insert(0, '..')
import time


def app():
    """
    In this page, we will do scenario analysis for a selected property.
    """
    with open('data/selected_properties.pkl', 'rb') as f:
        zpid = pickle.load(f)
    df = pd.read_csv('data/search_data_with_metrics.csv')
    address = df.loc[df["zpid"] == zpid, "Address"].values[0]
    price = df.loc[df["zpid"] == zpid, "Price"].values[0]
    irr_u = df.loc[df["zpid"] == zpid, "IRR (unleveraged)"].values[0]
    irr_l = df.loc[df["zpid"] == zpid, "IRR (leveraged)"].values[0]
    cap_rate = df.loc[df["zpid"] == zpid, "Cap Rate"].values[0]
    coc = df.loc[df["zpid"] == zpid, "Cash On Cash Return"].values[0]

    st.markdown("<h1 style='text-align: center; color: black;'>Investment Scenario Analysis</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: grey;'>You've selected <strong style='color:red'>{address}</strong> property for this analysis.</p>", unsafe_allow_html=True)

    st.markdown("#")
    with st.container():
        irr_u_delta = 0
        irr_l_delta = 0
        cap_rate_delta = 0
        coc_delta = 0
        irr_u_original = irr_u
        irr_l_original = irr_l
        cap_rate_original = cap_rate
        coc_original = coc
        c1, c2, c3, c4 = st.columns([1,1,1,1])
        c1.metric("IRR (unleveraged)", f"{irr_u_original} %")
        c2.metric("IRR (leveraged)", f"{irr_l_original} %")
        c3.metric("Cap Rate", f"{cap_rate_original} %")
        c4.metric("Cash On Cash Return", f"{coc_original} %")

        st.markdown("#")
        # st.markdown("---")
        # st.markdown("#")
    with st.expander("Scenario Description"):
        with st.form("Modify Assumptions"):
            modified_assumptions = {
                'eqt_pct': 0.5,
                'cash_reserves': 2_500,
                'amort_period': 30,
                'int_rate': 0.05,
                'renov_cost': 3_000,
                'renov_period': 4,
                'exit_renov_cost': 3_000,
                'length_of_hold': 7,
                'appreciation_rate': 0.02,
                'vacan_rate': 0.0775,
                'property_manager_rate': 0.01,
                'utilities': 40,
            }

            st.markdown("<h4 style='text-align: center; color: black;'>Modify investment assumptions and hit Submit!</h4>", unsafe_allow_html=True) 
            with st.container():
                c1, c2, c3, c4 = st.columns([1,1,1,1])
                eqt_pct = c1.number_input("Equity Percentage", value=modified_assumptions['eqt_pct'])
                cash_reserves = c2.number_input("Cash Reserves", value=modified_assumptions['cash_reserves'])
                amort_period = c3.number_input("Amortization Period", value=modified_assumptions['amort_period'])
                int_rate = c4.number_input("Interest Rate", value=modified_assumptions['int_rate'])

            with st.container():
                c1, c2, c3, c4 = st.columns([1,1,1,1])
                renov_cost = c1.number_input("Renovation Cost", value=modified_assumptions['renov_cost'])
                renov_period = c2.number_input("Renovation Period", value=modified_assumptions['renov_period'])
                exit_renov_cost = c3.number_input("Exit Renovation Cost", value=modified_assumptions['exit_renov_cost'])
                length_of_hold = c4.number_input("Length of Hold", value=modified_assumptions['length_of_hold'])

            with st.container():
                c1, c2, c3, c4 = st.columns([1,1,1,1])
                appr_rate = c1.number_input("Appreciation Rate", value=modified_assumptions['appreciation_rate'])
                vacancy = c2.number_input("Vacancy Rate", value=modified_assumptions['vacan_rate'])
                prop_manager = c3.number_input("Property Manager Rate", value=modified_assumptions['property_manager_rate'])
                utilities = c4.number_input("Utilities", value=modified_assumptions['utilities'])

            st.markdown("#")
            with st.container():
                c1, c2, c3 = st.columns([4,1,4])
                with c1:
                    st.write('')
                with c2:
                    submit_button = st.form_submit_button("Submit")
                with c3:
                    st.write('')
                if submit_button:
                    modified_assumptions['eqt_pct'] = eqt_pct
                    modified_assumptions['cash_reserves'] = cash_reserves
                    modified_assumptions['amort_period'] = amort_period
                    modified_assumptions['int_rate'] = int_rate
                    modified_assumptions['renov_cost'] = renov_cost
                    modified_assumptions['renov_period'] = renov_period
                    modified_assumptions['exit_renov_cost'] = exit_renov_cost
                    modified_assumptions['length_of_hold'] = length_of_hold
                    modified_assumptions['appreciation_rate'] = appr_rate
                    modified_assumptions['vacan_rate'] = vacancy
                    modified_assumptions['property_manager_rate'] = prop_manager
                    modified_assumptions['utilities'] = utilities
                    # st.write(f"You've modified the following assumptions:")
                    # st.write(modified_assumptions)
                    # st.write(f"<h4 style='text-align: center; color: black;'>Modify investment assumptions and hit Submit!</h4>", unsafe_allow_html=True) 
                    with open('data/modified_assumptions.json', 'w') as f:
                        json.dump(modified_assumptions, f)

    # calculating the metrics based on new assumptions
    with open('data/modified_assumptions.json', 'r') as f:
        modified_assumptions = json.load(f)
    ie = InvestmentAssumptions()
    ie.eqt_pct = modified_assumptions['eqt_pct']
    ie.extra_cash_reserves = modified_assumptions['cash_reserves']
    ie.amort_period = modified_assumptions['amort_period']
    ie.int_rate_on_debt = modified_assumptions['int_rate']
    ie.renovation_costs = modified_assumptions['renov_cost']
    ie.renovation_period = modified_assumptions['renov_period']
    ie.exit_renovation_cost = modified_assumptions['exit_renov_cost']
    ie.length_of_hold = modified_assumptions['length_of_hold']
    ie.appreciation_rate = modified_assumptions['appreciation_rate']
    ie.vacancy_rate = modified_assumptions['vacan_rate']
    ie.property_manager_rate = modified_assumptions['property_manager_rate']
    ie.utilities = modified_assumptions['utilities']

    dp = DataPrep(zpid, investment_assumptions=ie)
    cash_flow = dp.get_cashflow()
    cash_flow_unleveraged = cash_flow['cash_flow_unleveraged']
    cash_flow_leveraged = cash_flow['cash_flow_leveraged']
    dates = cash_flow['dates']
    dates_xirr = Metrics.xirr_dates(dates)

    irr_u_new = np.round((Metrics.xirr(values=cash_flow_unleveraged, dates=dates_xirr))*100, 2)
    irr_l_new = np.round((Metrics.xirr(values=cash_flow_leveraged, dates=dates_xirr))*100, 2)
    cap_rate_new = Metrics.cap_rate(cash_flow['net_rents'], price)
    coc_new = Metrics.cash_on_cash_return(cash_flow['net_rents'], cash_flow['less_taxes'], cash_flow['cash_invested'])
    
    irr_u_delta = np.round(((irr_u_new - irr_u_original) / irr_u_original)*100, 2)
    irr_l_delta = np.round(((irr_l_new - irr_l_original) / irr_l_original)*100, 2)
    cap_rate_delta = np.round(((cap_rate_new - cap_rate_original) / cap_rate_original)*100, 2)
    coc_delta = np.round(((coc_new - coc_original) / coc_original)*100, 2)

    st.markdown("#")
    with st.container():
        c1, c2, c3, c4 = st.columns([1,1,1,1])
        c1.metric("IRR (unleveraged)", f"{irr_u_new} %", f"{irr_u_delta} %")
        c2.metric("IRR (leveraged)", f"{irr_l_new} %", f"{irr_l_delta} %")
        c3.metric("Cap Rate", f"{cap_rate_new} %", f"{cap_rate_delta} %")
        c4.metric("Cash On Cash Return", f"{coc_new} %", f"{coc_delta} %")
        # irr_u = irr_u_new
        # irr_l = irr_l_new
        # cap_rate = cap_rate_new
        # coc = coc_new
        st.markdown("#")

    st.markdown("#")
    with st.container():
        c1, c2 = st.columns([1,1])
        with c1:
            dates = cash_flow['dates'][1:12]
            c_u = cash_flow['cash_flow_unleveraged'][1:12]
            fig = px.bar(x=dates, y=c_u, labels={"x": "Year", "y": "Cash Flow"}, text=c_u, title="Unleveraged Cash Flow")
            fig.update_layout(title_x=0.5)
            st.plotly_chart(fig)
        with c2:
            dates = cash_flow['dates'][1:12]
            c_l = cash_flow['cash_flow_leveraged'][1:12]
            fig = px.bar(x=dates, y=c_l, labels={"x": "Year", "y": "Cash Flow"}, text=c_l, title="Leveraged Cash Flow")
            fig.update_layout(title_x=0.5)
            st.plotly_chart(fig)