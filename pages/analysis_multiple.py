import sys
sys.path.insert(0, '.')
sys.path.insert(0, '..')

import streamlit as st
import json
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.express as px
import pickle
from src.utils import DataPrep, InvestmentAssumptions
from src.metrics import Metrics
from src.config import *
import time


def delta_metrics(orig, new):
    return np.round(((new - orig) / orig)*100, 2)


def update_metrics(modified_assumptions, price, zpid):
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
    return irr_u_new, irr_l_new, cap_rate_new, coc_new, cash_flow


def app():
    """
    In this page, we will do scenario analysis for a selected property.
    """
    # with open(f'{BASE_DIR}/{SELECTED_PROPERTY}', 'rb') as f:
    #     zpid = pickle.load(f)
    zpid_selected = [111962375, 63395420]
    with open(f'{BASE_DIR}/{USER_FINANCE}', 'r') as f:
        user_finance = json.load(f)
    df = pd.read_csv(f'{BASE_DIR}/{PROP_SEARCH_WITH_METRICS_FILTERED}')
    address, price, irr_u, irr_l, cap_rate, coc = [], [], [], [], [], []
    for zpid in zpid_selected:
        address.append(df.loc[df["zpid"] == zpid, "Address"].values[0])
        price.append(df.loc[df["zpid"] == zpid, "Price"].values[0])
        irr_u.append(df.loc[df["zpid"] == zpid, "IRR (unleveraged)"].values[0])
        irr_l.append(df.loc[df["zpid"] == zpid, "IRR (leveraged)"].values[0])
        cap_rate.append(df.loc[df["zpid"] == zpid, "Cap Rate"].values[0])
        coc.append(df.loc[df["zpid"] == zpid, "Cash On Cash Return"].values[0])

    # initial metric values based on non-modified assumptions
    if 'irr_u' not in st.session_state:
        st.session_state["irr_u"] = irr_u
    if 'irr_l' not in st.session_state:
        st.session_state["irr_l"] = irr_l
    if 'cap_rate' not in st.session_state:
        st.session_state["cap_rate"] = cap_rate
    if 'coc' not in st.session_state:
        st.session_state["coc"] = coc
    if 'irr_u_delta' not in st.session_state:
        st.session_state["irr_u_delta"] = [0]*len(irr_u)
    if 'irr_l_delta' not in st.session_state:
        st.session_state["irr_l_delta"] = [0]*len(irr_l)
    if 'cap_rate_delta' not in st.session_state:
        st.session_state["cap_rate_delta"] = [0]*len(cap_rate)
    if 'coc_delta' not in st.session_state:
        st.session_state["coc_delta"] = [0]*len(coc)
    if 'cash_flow' not in st.session_state:
        st.session_state["cash_flow"] = [None]*len(coc)

    st.markdown("<h1 style='text-align: center; color: black;'>Investment Scenario Analysis</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: grey;'>You've selected <strong style='color:red'>{address}</strong> property for this analysis.</p>", unsafe_allow_html=True)

    for i in range(len(zpid_selected)):
        st.markdown("#")
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([3,2,2,2,2])
            c1.subheader(f"Property {i+1}")
            c1.caption(f"{address[i]}")
            c2.metric("IRR (unleveraged)", f"{st.session_state.irr_u[i]} %", f"{st.session_state.irr_u_delta[i]} %")
            c3.metric("IRR (leveraged)", f"{st.session_state.irr_l[i]} %", f"{st.session_state.irr_l_delta[i]} %")
            c4.metric("Cap Rate", f"{st.session_state.cap_rate[i]} %", f"{st.session_state.cap_rate_delta[i]} %")
            c5.metric("Cash On Cash Return", f"{st.session_state.coc[i]} %", f"{st.session_state.coc_delta[i]} %")

            # st.markdown("#")
            st.markdown("---")
            # st.markdown("#")

    with st.expander("Scenario Description"):
        # with st.form("Modify Assumptions"):
        modified_assumptions = {
            'eqt_pct': user_finance['eqt_pct'],
            'cash_reserves': user_finance['extra_cash_reserves'],
            'amort_period': user_finance['amort_period'],
            'int_rate': user_finance['int_rate_on_debt'],
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
            eqt_pct = c1.number_input("Equity Percentage", value=modified_assumptions['eqt_pct'], help="Down payment percentage")
            cash_reserves = c2.number_input("Cash Reserves", value=modified_assumptions['cash_reserves'])
            amort_period = c3.number_input("Amortization Period", value=modified_assumptions['amort_period'], help="Mortgage period in years")
            int_rate = c4.number_input("Interest Rate", value=modified_assumptions['int_rate'], help="Interest rate on the mortgage")

        with st.container():
            c1, c2, c3, c4 = st.columns([1,1,1,1])
            renov_cost = c1.number_input("Renovation Cost", value=modified_assumptions['renov_cost'], help="Renovation cost required after the purchase")
            renov_period = c2.number_input("Renovation Period", value=modified_assumptions['renov_period'], help="How long will the renovation take? (in months)")
            exit_renov_cost = c3.number_input("Exit Renovation Cost", value=modified_assumptions['exit_renov_cost'], help="How much are planning to spend on renovation at the time of selling?")
            length_of_hold = c4.number_input("Length of Hold", value=modified_assumptions['length_of_hold'], help="How long will the property be on hold? (in years)")

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
                # submit_button = st.form_submit_button("Submit")
                submit_button = st.button("Submit")
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

                with open(f'{BASE_DIR}/{USER_ASSUMPTIONS_MODIFIED}', 'wb') as f:
                    pickle.dump(modified_assumptions, f)

                # calculating the metrics based on new assumptions
                irr_u_new_lst, irr_l_new_lst, cap_rate_new_lst, coc_new_lst = [], [], [], []
                irr_u_delta_lst, irr_l_delta_lst, cap_rate_delta_lst, coc_delta_lst = [], [], [], []
                for i, zpid in enumerate(zpid_selected):
                    irr_u_new, irr_l_new, cap_rate_new, coc_new, cash_flow = update_metrics(modified_assumptions, price[i], zpid)
                    irr_u_new_lst.append(irr_u_new)
                    irr_l_new_lst.append(irr_l_new)
                    cap_rate_new_lst.append(cap_rate_new)
                    coc_new_lst.append(coc_new)
                    irr_u_delta_lst.append(delta_metrics(st.session_state.irr_u[i], irr_u_new))
                    irr_l_delta_lst.append(delta_metrics(st.session_state.irr_l[i], irr_l_new))
                    cap_rate_delta_lst.append(delta_metrics(st.session_state.cap_rate[i], cap_rate_new))
                    coc_delta_lst.append(delta_metrics(st.session_state.coc[i], coc_new))

                st.session_state.irr_u_delta = irr_u_delta_lst
                st.session_state.irr_l_delta = irr_l_delta_lst
                st.session_state.cap_rate_delta = cap_rate_delta_lst
                st.session_state.coc_delta = coc_delta_lst
                st.session_state.irr_u = irr_u_new_lst
                st.session_state.irr_l = irr_l_new_lst
                st.session_state.cap_rate = cap_rate_new_lst
                st.session_state.coc = coc_new_lst

    # st.markdown("#")
    # with st.container():
    #     if st.session_state.cash_flow is not None:
    #         c1, c2 = st.columns([1,1])
    #         with c1:
    #             dates = st.session_state.cash_flow['dates'][1:12]
    #             c_u = st.session_state.cash_flow['cash_flow_unleveraged'][1:12]
    #             fig = px.bar(x=dates, y=c_u, labels={"x": "Year", "y": "Cash Flow"}, text=c_u, title="Unleveraged Cash Flow")
    #             fig.update_layout(title_x=0.5)
    #             st.plotly_chart(fig)
    #         with c2:
    #             dates = st.session_state.cash_flow['dates'][1:12]
    #             c_l = st.session_state.cash_flow['cash_flow_leveraged'][1:12]
    #             fig = px.bar(x=dates, y=c_l, labels={"x": "Year", "y": "Cash Flow"}, text=c_l, title="Leveraged Cash Flow")
    #             fig.update_layout(title_x=0.5)
    #             st.plotly_chart(fig)
    #     else:
    #         st.write("")