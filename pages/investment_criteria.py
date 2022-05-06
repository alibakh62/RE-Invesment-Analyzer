import streamlit as st
import json
import sys
sys.path.insert(0, '.')
sys.path.insert(0, '..')


def app():
    """
    In this page, user can see the default assumptions for the project.
    """
    st.markdown("<h1 style='text-align: center; color: black;'>Tell us how you want to invest.</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: grey;'>We use this information to find properties and calculate their return metrics.</p>", unsafe_allow_html=True)

    user_metrics = {}
    user_finance = {}

    with st.container():    
        c1, c2, c3 = st.columns([1,1,1])
        with c1:
            inv_type = st.selectbox("Investment Type", ["Residential", "Commercial"], key="inv_type")
        with c2:
            if st.session_state.inv_type == "Residential":
                list_of_metrics = ["Cap Rate", "Cash On Cash Return", "IRR Unleveraged", "IRR Leveraged"]
            elif st.session_state.inv_type == "Commercial":
                list_of_metrics = ["Metric 1", "Metric 2", "Metric 3", "Metric 4"]
            inv_metric = st.selectbox(label="Select the investment metric:", options=list_of_metrics, key="inv_metric_select")
        with c3:
            min_inv_metric = st.slider(label=f"Choose minimum {st.session_state.inv_metric_select} (%)", min_value=0, max_value=100, key="min_inv_metric")

    with st.expander("Metric Definition:"):
        c1, c2, c3 = st.columns([1,1,1])
        with c1:
            if st.session_state.inv_metric_select == "Cap Rate":
                st.markdown('**Capitalization rate** indicates the rate of return that is expected to be generated on a real estate investment property, [more](https://www.investopedia.com/terms/c/capitalizationrate.asp) ')
                st.write('')
                st.latex(r'''\text{Cap Rate} = \frac{\text{Net Operating Income}}{\text{Current Market Value}}''')
            elif st.session_state.inv_metric_select == "Cash On Cash Return":
                st.markdown('**Cash-on-cash return** measures the annual return the investor made on the property in relation to the amount of mortgage paid during the same year, [more](https://www.investopedia.com/terms/c/cashoncashreturn.asp) ')
                st.write('')
                st.latex(r'''\text{Cash On Cash Return} = \frac{\text{Annual Pre-Tax Cash Flow}}{\text{Total Cash Invested}}''')
                st.write('')
                st.markdown('***where:***')
                st.latex(r'''\text{Annual Pre-Tax Cash Flow} = \text{Gross scheduled rent} + \text{Other income} - \text{Vacancy} - \text{Other expenses} - \text{Annual mortgage payments}''')
            elif (st.session_state.inv_metric_select == "IRR Unleveraged") | (st.session_state.inv_metric_select == "IRR Leveraged"):
                st.markdown('**IRR** is a discount rate that makes the net present value (NPV) of all cash flows equal to zero in a discounted cash flow analysis, [more](https://www.investopedia.com/terms/i/irr.asp) ')
                st.write('')
                st.latex(r'''0 = \text{NPV} = \sum\limits_{t=1}^{T} \frac{C_{t}}{(1+\text{IRR})^t} - C_0''')
            else:
                st.markdown("<p style='text-align: center; color: black;'>$Other definitions$</p>", unsafe_allow_html=True)

    with st.container():
        st.markdown("""---""")

    with st.container():
        c1, c2, c3 = st.columns([1,1,1])
        c2.markdown("<h3 style='text-align: center; color: black;'>Financials</h3>", unsafe_allow_html=True)
        with c1:
            st.write('')
        with c2:
            eqt_pct = st.number_input("How much are planning to pay as down payment? (as % of purchase price)", value=0.5, key="eqt_pct")
            amort_period = st.number_input("What mortgage duration (years) are you considering?", value=30, step=1, key="amort_period")
            int_rate_on_debt = st.number_input("What's your mortgage rate?(%)", value=0.05, key="int_rate_on_debt")
            extra_cash_reserves = st.number_input("How much cash reserves you have? ($)", value=2500, step=1_000, help="This refers to any liquid assests you have leftover after paying your down payment and closing costs.", key="extra_cash_reserves")
        with c3:
            st.write('')

    with st.container():
        st.markdown("#")

    with st.container():
        c1, c2, c3 = st.columns([6,1,6])

        with c1:
            st.write('')
        with c2:
            submit_all = st.button("Submit", key="submit_all")
            if submit_all:
                user_metrics['metric_selected'] = st.session_state.inv_metric_select
                user_metrics['metric_min'] = st.session_state.min_inv_metric
                user_finance['eqt_pct'] = st.session_state.eqt_pct
                user_finance['amort_period'] = st.session_state.amort_period
                user_finance['int_rate_on_debt'] = st.session_state.int_rate_on_debt
                user_finance['extra_cash_reserves'] = st.session_state.extra_cash_reserves
                with open('data/user_metrics_new.json', 'w') as f:
                    json.dump(user_metrics, f)
                with open('data/user_finance_new.json', 'w') as f:
                    json.dump(user_finance, f)
        with c3:
            st.write('')

    with st.container():
        c1, c2, c3 = st.columns([1,1,1])
        with c1:
            st.write('')
            # st.write(user_metrics)
        with c2:
            if st.session_state.submit_all:
                st.success("Your selections have been saved.")
        with c3:
            st.write('')
            # st.write(user_finance)