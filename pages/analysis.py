import pandas as pd
import numpy as np
import numpy_financial as npf
from datetime import datetime

from scipy.optimize import anderson
from datetime import datetime

import streamlit as st
import json
import sys
sys.path.insert(0, '.')
sys.path.insert(0, '..')

global user_assumptions

with open('data/user_assumptions_test.json', 'r') as f:
    user_assumptions = json.load(f)

def cumulative(lists):
    cu_list = []
    length = len(lists)
    cu_list = [sum(lists[0:x:1]) for x in range(0, length+1)]
    return np.sum(cu_list[1:])


def calc_rent_cash_flow(months, monthly_gross_rent, rental_growth_rate, lease_up, exit_sale, project_life):
    rent_cash_flow = []
    rent_cash_flow.append(lease_up[0]*monthly_gross_rent)
    for i in range(1, len(months)):
        rent_cash_flow.append(int(np.round(max(lease_up[i]*monthly_gross_rent*(1+rental_growth_rate[i]), (rent_cash_flow[i-1]*(1+rental_growth_rate[i])))*project_life[i], 0)))
    return rent_cash_flow


def xnpv(rate, values, dates):
    
    if rate <= -1.0:
        return float('inf')
    min_date = min(dates)
    return sum([
        value / (1 + rate)**((date - min_date).days / 365)
        for value, date
        in zip(values, dates)
     ])


def xirr(values, dates):
    return anderson(lambda r: xnpv(r, values, dates), 0)


def run_analysis(user_assumptions):
    """
    Analyzes a property and returns a dictionary of metrics
    """
    # -- Core Deal Assumptions
    monthly_gross_rent = 1_500
    purchase_price = 120_000
    purchase_date = datetime.now().strftime('%Y-%m-%d')  # by default we're getting today's date
    closing_costs_ = int(0.016675*purchase_price)  # typically 1-2% of purchase price

    extra_cash_reserves = 2_500

    # -- Renovations
    renovation_costs = 1_500
    renovation_period = 4  # lease up window in months
    exit_renovation_cost = 5_000

    total_project_cost = purchase_price + closing_costs_ + renovation_costs + exit_renovation_cost

    # -- Financing
    equity_pct = 0.5
    total_equity_investment = int(equity_pct*total_project_cost)
    total_project_loan_amount = int((1-equity_pct)*total_project_cost)
    amortization_period = 30  # years
    interest_rate_on_debt = 0.055

    # -- Exit Assumptions
    MAX_HOLD = 7  # maximum holding period in years
    length_of_hold = 7  # years
    appreciation = 0.02  # annual
    sales_price_at_exit = int(purchase_price*(1 + appreciation)**min(MAX_HOLD, length_of_hold))  # value of property at exit
    cost_of_sale = 0.06  # broker fees & closing costs

    # -- Other Assumptions
    vacancy_rate = 0.0775 # annual, 7.75% means 4 weeks vacancy
    vacancy_weeks = np.round(vacancy_rate*52, 1)
    rent_growth_rate = 0.03 # annual
    repair_allowance = 0.07 # monthly
    repair_allowance_amount = int(repair_allowance*monthly_gross_rent*12) # annual
    property_taxes = 1_500 # annual
    insurance = 500 # annual
    property_manager_rate = 0.0 # monthly
    property_manager_amount = int(property_manager_rate*monthly_gross_rent) # per month starting year 1
    utilities = 40 # monthly, it'll be $0 if tenant is paying
    discount_rate = 0.075  # for calculating NPV

    # -- Uses
    total_uses = int(purchase_price + closing_costs_ + renovation_costs + exit_renovation_cost)

    # -- Sources
    equity = int(total_uses - total_project_loan_amount)

    # -- Timing
    dates = pd.date_range(start=purchase_date, periods=int(12*length_of_hold), freq='M').strftime('%Y-%m-%d').tolist()
    months_numbers = [datetime.strptime(d, '%Y-%m-%d').month for d in dates]
    months = [i+1 for i in range(len(months_numbers))]
    lease_up = [0 if months[i] <= renovation_period else 1 for i in range(len(months))] 
    exit_sale = [0 if np.round(min(min(np.round(length_of_hold, 0), 7), 7), 0)*12 != months[i] else 1 for i in range(len(months))]
    project_life = [0 if cumulative(exit_sale[:i]) == 1 else 1 for i in range(len(exit_sale))]

    # -- Rent Assumptions
    rental_growth_rate = [rent_growth_rate if (months[i] % 12) == 0 else 0 for i in range(len(months))]
    vacancy = [vacancy_rate for i in range(len(months))]

    # -- Project Costs
    closing_costs = [0 for i in range(len(months))]
    closing_costs[0] = -closing_costs_
    purchase_costs = [0 for i in range(len(months))]
    purchase_costs[0] = -purchase_price
    renovations0 = [-renovation_costs//renovation_period if months[i] <= renovation_period else 0 for i in range(len(months))]
    renovations1 = [exit_renovation_cost if months[i] == min(length_of_hold, MAX_HOLD)*12 else 0 for i in range(len(months))]
    renovations = [renovations0[i]-renovations1[i] for i in range(len(months))]

    total_project_costs = [closing_costs[i]+purchase_costs[i]+renovations[i] for i in range(len(months))]

    # -- Net Rents
    cash_invested = [0 for i in range(len(months))]
    cash_invested[0] = total_equity_investment
    extra_reserves = [0 for i in range(len(months))]
    extra_reserves[0] = extra_cash_reserves

    rents = calc_rent_cash_flow(months, monthly_gross_rent, rental_growth_rate, lease_up, exit_sale, project_life)
    less_management_fees = [property_manager_rate*rents[i] for i in range(len(months))]
    less_vacancy = [vacancy_rate*rents[i] for i in range(len(months))]
    less_repairs = [repair_allowance*rents[i] for i in range(len(months))]
    less_taxes = [property_taxes*project_life[i] if i % 12 == 0 else 0 for i in range(len(months))]
    less_insurance = [insurance*project_life[i] if i % 12 == 0 else 0 for i in range(len(months))]
    less_utilities = [lease_up[i]*project_life[i]*utilities for i in range(len(months))]

    net_rents = [int(np.round(rents[i]-less_management_fees[i]-less_vacancy[i]-less_repairs[i]-less_taxes[i]-less_insurance[i]-less_utilities[i], 0)) for i in range(len(months))]

    # -- Amortization
    rate_per_period = (1 + interest_rate_on_debt/12)**(12/12) - 1
    number_of_payments = 360  #TODO: get this from amortization
    monthly_payment = -np.round(npf.pmt(rate= interest_rate_on_debt/ 12, nper=amortization_period * 12, pv=total_project_loan_amount, fv=0, when='end'), 2)
    amortization_date = pd.date_range(start=purchase_date, periods=int(12*amortization_period), freq='M').strftime('%Y-%m-%d').tolist()
    payment_no = [i+1 for i in range(len(amortization_date))]
    amortization_month = [i+1 if i <= len(months)-1 else 0 for i in range(len(amortization_date))]
    amortization_interest = []
    amortization_balance = []
    amortization_principal = []
    amortization_additional_payment = []

    for i in range(len(amortization_date)):
        if i == 0:
            amortization_interest.append(0)
            amortization_balance.append(total_project_loan_amount)
            amortization_principal.append(0)
            amortization_additional_payment.append(0)
        else:
            amortization_interest.append(np.round(amortization_balance[i-1]*rate_per_period, 2))
            amortization_principal.append(np.round(monthly_payment - amortization_interest[i], 2))
            amortization_additional_payment.append(0)
            amortization_balance.append(np.round(amortization_balance[i-1] - amortization_principal[i] - amortization_additional_payment[i], 2))

    # -- Loan Principal
    interest = [np.round(amortization_interest[i+1], 0) for i in range(len(months))]
    interest_paid_from_rents = [max(0, min(net_rents[i], interest[i])) for i in range(len(months))]
    interest_paid_from_account = [interest[i]-interest_paid_from_rents[i] if net_rents[i] < interest[i] else 0 for i in range(len(months))]
    principal_amount = [np.round(amortization_principal[i+1], 0) for i in range(len(months))]
    principal_paid_from_rents = [max(0, min(principal_amount[i], net_rents[i]-interest_paid_from_rents[i])) for i in range(len(months))]
    principal_paid_from_account = [principal_amount[i]-principal_paid_from_rents[i] if principal_amount[i] > principal_paid_from_rents[i] else 0 for i in range(len(months))]
    principal_paid_from_sale = [0 for i in range(len(months))]  #TODO: it's -debt

    loan_principal = []
    for i in range(len(months)):
        if i == 0:
            loan_principal.append(total_project_loan_amount)
        else:
            loan_principal.append(np.round(max(0, loan_principal[i-1] + interest[i-1] - interest_paid_from_rents[i-1] - interest_paid_from_account[i-1]- principal_paid_from_rents[i-1] - principal_paid_from_account[i-1] - principal_paid_from_sale[i-1]), 0))

    net_rent_debt_services = [net_rents[i]-interest_paid_from_rents[i]-principal_paid_from_rents[i] for i in range(len(months))]

    # -- Net Rents - Debt Services
    debt_service_paid = []
    less_reserves = []
    net_rent_deposits = []
    bank_account = []
    for i in range(len(months)):
        if i == 0:
            bank_account.append(cash_invested[i] + extra_reserves[i] + net_rents[i])
            debt_service_paid.append(min(bank_account[i], interest_paid_from_account[i] + principal_paid_from_account[i]))
            less_reserves.append(min(0, net_rents[i] + total_project_costs[i] + loan_principal[i]))
            net_rent_deposits.append(max(0, net_rent_debt_services[i]))
        else:
            bank_account.append(bank_account[i-1] - debt_service_paid[i-1] + less_reserves[i-1] + net_rent_deposits[i-1])
            debt_service_paid.append(min(bank_account[i], interest_paid_from_account[i] + principal_paid_from_account[i]))
            less_reserves.append(min(0, net_rents[i] + total_project_costs[i]))
            net_rent_deposits.append(max(0, net_rent_debt_services[i] - principal_paid_from_account[i] - interest_paid_from_account[i]))

    sales_price = [0 for i in range(len(months))]
    sales_price[-1] = sales_price_at_exit
    less_cost_of_sales = [cost_of_sale*sales_price[i] for i in range(len(months))]
    less_debt = [min(sales_price[i]-less_cost_of_sales[i], loan_principal[i]+interest[i]-interest_paid_from_rents[i]-principal_paid_from_rents[i]) for i in range(len(months))]
    net_proceeds = [np.round(sales_price[i]-less_cost_of_sales[i]-less_debt[i], 0) for i in range(len(months))]

    # -- Cash Flow
    cash_flow_unleveraged = []
    cash_flow_leveraged = []

    for i in range(len(months)):
        if i == 0:
            cash_flow_unleveraged.append(total_project_costs[i]+extra_reserves[i]+net_rents[i]+sales_price[i]-less_cost_of_sales[i])
            if equity_pct == 1:
                unlevered_amt = cash_flow_unleveraged[i]
            else:
                unlevered_amt = -cash_invested[i] + net_rents[i] - extra_reserves[i]
            cash_flow_leveraged.append(unlevered_amt)
        else:
            cash_flow_unleveraged.append(total_project_costs[i]+net_rents[i]+sales_price[i]-less_cost_of_sales[i])
            if equity_pct == 1:
                unlevered_amt = cash_flow_unleveraged[i]
            else:
                unlevered_amt = net_rent_debt_services[i] + net_proceeds[i]
            cash_flow_leveraged.append(unlevered_amt)

    dates_xirr = [datetime.strptime(i, '%Y-%m-%d').date() for i in dates]
    irr_unleveraged = np.round(xirr(values=cash_flow_unleveraged, dates=dates_xirr)*100, 2)
    irr_leveraged = np.round(xirr(values=cash_flow_leveraged, dates=dates_xirr)*100, 2)
    return irr_leveraged, irr_unleveraged



def app():
    """
    This is where user searches for properties
    """
    st.title("Analysis")
    st.write("Welcome to the analysis page")

    irr_leveraged, irr_unleveraged = run_analysis(user_assumptions)

    # user_assumptions = json.load(open('../data/user_assumptions.json'))
    with st.form("my_form"):
        st.write("Sample scenario widgets")
        slider_val = st.slider("Form slider")
        checkbox_val = st.checkbox("Form checkbox")

        st.write("Results will be shown here")
        st.metric("IRR - Unleveraged", irr_unleveraged, delta=None, delta_color="normal")
        st.metric("IRR - Leveraged", irr_leveraged, delta=None, delta_color="normal")

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write("slider", slider_val, "checkbox", checkbox_val)

    st.write("Outside the form")