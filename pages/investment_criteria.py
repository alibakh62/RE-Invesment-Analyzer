import streamlit as st
import json
from datetime import datetime
import pandas as pd
import sys
sys.path.insert(0, '.')
sys.path.insert(0, '..')
import time

def handle_metric_select():
    if st.session_state.inv_metric_select == "Cap Rate":
        st.session_state.inv_metric_slider = "Please select min. Cap Rate (in %)"
    elif st.session_state.inv_metric_select == "Cash On Cash Return":
        st.session_state.inv_metric_slider = "Please select min. Cash On Cash Return (in %)"
    elif st.session_state.inv_metric_select == "IRR Unleveraged":
        st.session_state.inv_metric_slider = "Please select min. IRR Unleveraged (in %)"
    elif st.session_state.inv_metric_select == "IRR Leveraged":
        st.session_state.inv_metric_slider = "Please select min. IRR Leveraged (in %)"


def app():
    """
    In this page, user can see the default assumptions for the project.
    """
    st.markdown("<h1 style='text-align: center; color: black;'>Tell us how you want to invest.</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: grey;'>We use this information to find properties and calculate their return metrics.</p>", unsafe_allow_html=True)

    user_metrics = {}
    user_finance = {}

    with st.container():
        st.markdown("<p style='text-align: center; color: grey;'>Please choose what type of investment:</p>", unsafe_allow_html=True)

        with st.container():
            c1, c2, c3 = st.columns([3,1,3])

        with c1:
            st.write('')

        with c2:
            placeholder = st.empty()
            investment_type = placeholder.radio(label="", options=["Residential", "Commercial"], key="investment_type_radio")
            investment_type_submit = placeholder.button("Submit", key="inv_type_button")	

        with c3:
            st.write('')

        if st.session_state.inv_type_button:
            placeholder.empty()
            inv_metric_select = placeholder.selectbox("Choose the investment metric:", ["Cap Rate", "Cash On Cash Return", "IRR Unleveraged", "IRR Leveraged"], on_change=handle_metric_select(), key="inv_metric_select")
            inv_metric_min = placeholder.slider(label=st.session_state.inv_metric_slider, min_value=0, max_value=100, step=1, value=0, key="inv_metric_slider")


    # with st.container():
    #     c1, c2, c3 = st.columns([1,2,1])
    #     # c1.markdown("<h3 style='text-align: center; color: black;'>Financing</h3>", unsafe_allow_html=True)
    #     c2.markdown("<h3 style='text-align: center; color: black;'>Investment Criteria</h3>", unsafe_allow_html=True)
    #     # c3.markdown("<h3 style='text-align: center; color: black;'>Renovation Costs</h3>", unsafe_allow_html=True)
    #     with c1:
    #         st.write('')
    #     with c2:
    #         with st.form("Investment Criteria"):
    #             cap_rate = st.slider("Min. Cap Rate (%)", min_value=0.0, max_value=1.0, value=0.25, step=0.01)
    #             coc = st.slider("Min. Cash on Cash Return (%)", min_value=0.0, max_value=1.0, value=0.25, step=0.01)
    #             irr_leveraged = st.slider("Min. IRR Leveraged (%)", min_value=0.0, max_value=1.0, value=0.25, step=0.01)
    #             irr_unleveraged = st.slider("Min. IRR Unleveraged (%)", min_value=0.0, max_value=1.0, value=0.25, step=0.01)
    #             submitted_financing = st.form_submit_button("Submit")
    #             if submitted_financing:
    #                 user_metrics['cap_rate'] = cap_rate
    #                 user_metrics['coc'] = coc
    #                 user_metrics['irr_leveraged'] = irr_leveraged
    #                 user_metrics['irr_unleveraged'] = irr_unleveraged
    #                 with open('data/user_metrics.json', 'w') as f:
    #                     json.dump(user_metrics, f)
    #                 st.success("Your metrics have been saved.")
    #     with c3:
    #         st.write('')

    # with st.container():
    #     st.markdown("""---""")

    # with st.container():
    #     c1, c2, c3 = st.columns([1,2,1])
    #     # c1.markdown("<h3 style='text-align: center; color: black;'>Financing</h3>", unsafe_allow_html=True)
    #     c2.markdown("<h3 style='text-align: center; color: black;'>Financials</h3>", unsafe_allow_html=True)
    #     # c3.markdown("<h3 style='text-align: center; color: black;'>Renovation Costs</h3>", unsafe_allow_html=True)
    #     with c1:
    #         st.write('')
    #     with c2:
    #         with st.form("Financing"):
    #             eqt_pct = st.number_input("How much are planning to pay as down payment? (as % of purchase price)", value=0.5)
    #             amort_period = st.number_input("What mortgage duration (years) are you considering?", value=30, step=1)
    #             int_rate_on_debt = st.number_input("What's your mortgage rate?(%)", value=0.05)
    #             extra_cash_reserves = st.number_input("How much cash reserves you have? ($)", value=2500, step=1_000, help="This refers to any liquid assests you have leftover after paying your down payment and closing costs.")
    #             submitted_financing = st.form_submit_button("Submit")
    #             if submitted_financing:
    #                 user_finance['extra_cash_reserves'] = extra_cash_reserves
    #                 user_finance['eqt_pct'] = eqt_pct
    #                 user_finance['amort_period'] = amort_period
    #                 user_finance['int_rate_on_debt'] = int_rate_on_debt
    #                 with open('data/user_finance.json', 'w') as f:
    #                     json.dump(user_finance, f)
    #                 st.success("Your financing details have been saved.")
    #     with c3:
    #         st.write('')