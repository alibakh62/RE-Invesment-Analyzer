import streamlit as st
import json
from datetime import datetime
import pandas as pd
import sys
sys.path.insert(0, '.')
sys.path.insert(0, '..')

def set_defaults():
    """
    Set default values for user_assumptions
    """
    appreciation_rate = 0.05
    length_of_hold = 7
    try:
        prop_data = pd.read_csv('data/prop_details.csv')
        asking_price = 300_000  #prop_data['price'].values[0]  #TODO: need to get selected property
        estimated_rent = 1_500  #prop_data['rentZestimate'].values[0]  #TODO: handle nan values
    except:
        asking_price = 300_000
        estimated_rent = 1500
    price_at_exit = int(asking_price*(1 + appreciation_rate)**min(7, length_of_hold))

    return {
        "appr_rate": appreciation_rate,
        "length_hold": length_of_hold,
        "sales_price_at_exit": price_at_exit,
        "monthly_gross_rent": estimated_rent,
        "asking_price": asking_price,
    }


def app():
    """
    This is where user searches for properties
    """
    default_values = set_defaults()
    user_assumptions = {}
    st.title("Investment Assumptions")
    st.write("Please set your assumptions below")

    with st.form("Core Assumptions"):
        st.write("These are core assumptions")
        monthly_gross_rent = st.number_input("Monthly Gross Rent", value=int(default_values["monthly_gross_rent"]), step=100)
        purchase_price = st.number_input("Purchase Price", value=int(default_values["asking_price"]), step=1_000)
        purchase_date = st.date_input("Purchase Date", value=datetime.now())
        purchase_date = purchase_date.strftime('%Y-%m-%d')
        closing_costs = st.number_input("Closing Costs", value=0, step=1_000, help="Typically 1-2% of purchase price")
        extra_cash_reserves = st.number_input("Extra Cash Reserves", value=2500, step=1_000, help="Typically 1-2% of purchase price")

        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write("Monthly Gross Rent", monthly_gross_rent, "Purchase Price", purchase_price, "Closing Costs", closing_costs)
            user_assumptions['monthly_gross_rent'] = monthly_gross_rent
            user_assumptions['purchase_price'] = purchase_price
            user_assumptions['purchase_date'] = purchase_date
            user_assumptions['closing_costs'] = closing_costs
            user_assumptions['extra_cash_reserves'] = extra_cash_reserves

    with st.form("Finance Assumptions"):
        st.write("These are finance assumptions")
        eqt_pct = st.number_input("Equity % of Total Project Cost", value=0.5)
        amort_period = st.number_input("Amortization Period (years)", value=30, step=1)
        int_rate_on_debt = st.number_input("Interest Rate (%) on Debt", value=0.05)

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write("equity percentage", eqt_pct, "amortization period", amort_period, "interest rate on debt", int_rate_on_debt)
            user_assumptions['eqt_pct'] = eqt_pct
            user_assumptions['amort_period'] = amort_period
            user_assumptions['int_rate_on_debt'] = int_rate_on_debt

    with st.form("Renovations"):
        st.write("These are renovation assumptions")
        renovation_costs = st.number_input("Renovation Costs", value=10_000, step=1_000)
        renovation_period = st.number_input("Renovation Period (months)", value=4, step=1)
        exit_renovation_cost = st.number_input("Exit Renovation Costs", value=5_000, step=1_000)

        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write("renovation costs", renovation_costs, "renovation period", renovation_period, "exit renovation costs", exit_renovation_cost)
            user_assumptions['renovation_costs'] = renovation_costs
            user_assumptions['renovation_period'] = renovation_period
            user_assumptions['exit_renovation_cost'] = exit_renovation_cost 


    with st.form("Exit Assumptions"):
        st.write("These are exit assumptions")
        length_hold = st.number_input("Length of Hold (years)", value=7, step=1)
        appr_rate = st.number_input("Appreciation Rate (%/year)", value=0.05)
        sales_price_at_exit = st.number_input("Sales Price at Exit ($)", value=int(default_values["sales_price_at_exit"]), step=1_000)
        cost_of_sale = st.number_input("Cost of Sale (%)", value=0.06, help="Cost of Sale includes broker fee and closing costs as a percentage of sales price")
        
        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write("Length of Hold (years)", length_hold, "Appreciation Rate (%/year)", appr_rate, "Sales Price at Exit ($)", sales_price_at_exit, "Cost of Sale (%)", cost_of_sale)
            user_assumptions['length_hold'] = length_hold
            user_assumptions['appr_rate'] = appr_rate
            user_assumptions['sales_price_at_exit'] = sales_price_at_exit
            user_assumptions['cost_of_sale'] = cost_of_sale

    with st.form("Other Assumptions"):
        st.write("These are other assumptions")
        vacancy_rate = st.number_input("Vacancy Rate (%/year)", value=0.0775, help="Vacancy rate is the percentage of the year that the property is vacant")
        rent_growth_rate = st.number_input("Rent Growth Rate (%/year)", value=0.02, help="Rent growth rate is the percentage increase in rent per year")
        repairs = st.number_input("Repairs (%/monthly)", value=0.07, help="Repairs and maintenance costs as a percentage of monthly rent")
        property_taxes = st.number_input("Property Taxes ($/year)", value=1_000, step=100)
        insurance = st.number_input("Insurance ($/year)", value=1_000, step=100)
        utilities = st.number_input("Utilities ($/month)", value=100, step=10)
        property_manager_fee = st.number_input("Property Manager Fee (%/month)", value=0.02, help="Property Manager Fee is the percentage of monthly rent charged to the property manager")
        discount_rate = st.number_input("Discount Rate (%)", value=0.05, help="Discount rate for calculating the NPV")

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write("Vacancy Rate (%/year)", vacancy_rate, "Rent Growth Rate (%/year)", rent_growth_rate, "Repairs (%/monthly)", repairs, "Property Taxes ($/year)", property_taxes, "Insurance ($/year)", insurance, "Utilities ($/month)", utilities, "Property Manager Fee (%/month)", property_manager_fee, "Discount Rate (%)", discount_rate)
            user_assumptions['vacancy_rate'] = vacancy_rate
            user_assumptions['rent_growth_rate'] = rent_growth_rate
            user_assumptions['repairs'] = repairs
            user_assumptions['property_taxes'] = property_taxes
            user_assumptions['insurance'] = insurance
            user_assumptions['utilities'] = utilities
            user_assumptions['property_manager_fee'] = property_manager_fee
            user_assumptions['discount_rate'] = discount_rate
    with st.form("Submit Assumptions"):
        st.write("If you agree with the above assumptions, click the button below to save your assumptions")
        submit_assumptions = st.form_submit_button("Submit Assumptions")
        if submit_assumptions:
            fn = json.dumps(user_assumptions)
            with open('data/user_assumptions.json', 'w') as f:
                f.write(fn)
            st.write("Successfully submitted! Go to the next page to do a final review of your assumptions.")