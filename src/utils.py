import sys
sys.path.insert(0, '.')
sys.path.insert(0, '..')

import numpy as np
import pandas as pd
import numpy_financial as npf
from datetime import datetime
import src.api as api

from scipy.optimize import anderson
import json

def cumulative(lists):
    cu_list = []
    length = len(lists)
    cu_list = [sum(lists[0:x:1]) for x in range(0, length+1)]
    return np.sum(cu_list[1:])

class InvestmentAssumptions:

    def __init__(self):
        self.search_filepath = '../data/search.csv'
        self.user_finance_filepath = '../data/user_finance.json'
        self.user_finance = None
        self.property_details = None
        self.rent_data = None
        self.search_data = None
        self.closing_costs_ = None
        # renovation assumptions
        self.renovation_costs = 3_000
        self.renovation_period = 4
        self.exit_renovation_cost = 3_000
        # exit assumptions
        self.MAX_HOLD = 7
        self.length_of_hold = 5
        self.appreciation = 0.02
        self.cost_of_sale = 0.06
        # other assumptions
        self.vacancy_rate = 0.0775
        self.rent_growth_rate = 0.03
        self.repair_allowance = 0.07
        self.property_manager_rate = 0.01
        self.utilities = 40
        self.discount_rate = 0.075


    def set_renovation_assumptions(self, renovation_costs, renovation_period, exit_renovation_cost):
        self.renovation_costs = renovation_costs
        self.renovation_period = renovation_period
        self.exit_renovation_cost = exit_renovation_cost

    def set_exit_assumptions(self, MAX_HOLD, length_of_hold, appreciation, cost_of_sale):
        self.MAX_HOLD = MAX_HOLD
        self.length_of_hold = length_of_hold
        self.appreciation = appreciation
        self.cost_of_sale = cost_of_sale

    def set_other_assumptions(self, closing_costs_, vacancy_rate, rent_growth_rate, repair_allowance, property_manager_rate, utilities, discount_rate):
        self.vacancy_rate = vacancy_rate
        self.rent_growth_rate = rent_growth_rate
        self.repair_allowance = repair_allowance
        self.property_manager_rate = property_manager_rate
        self.utilities = utilities
        self.discount_rate = discount_rate
        self.closing_costs_ = closing_costs_

    def get_listing_price(self, zpid):
        if self.search_data is None:
            self.search_data = pd.read_csv(self.search_filepath)
        return self.search_data.loc[self.search_data["zpid"] == zpid, "price"].values[0]

    def get_tax_rate(self, zpid):
        tax_info = {}
        if self.property_details is None:
            self.property_details = api.get_property_details(zpid).json()
        tax_info['tax_rate'] = self.property_details['propertyTaxRate']
        tax_info['tax_history'] = self.property_details['taxHistory']
        return tax_info

    def get_insurance(self, zpid):
        if self.property_details is None:
            self.property_details = api.get_property_details(zpid).json()
        return self.property_details['annualHomeownersInsurance']

    def get_rent_estimate(self, zpid):
        if self.rent_data is None:
            if self.search_data is None:
                self.search_data = pd.read_csv(self.search_filepath)
            property_type = self.search.loc[self.search["zpid"] == zpid, "propertyType"].values[0]
            address = self.search.loc[self.search["zpid"] == zpid, "address"].values[0]
            beds = self.search.loc[self.search["zpid"] == zpid, "bedrooms"].values[0]
            baths = self.search.loc[self.search["zpid"] == zpid, "bathrooms"].values[0]  

            # creating a mapping between standard property types across different APIs
            property_type0 = ["SINGLE_FAMILY", "CONDO", "TOWNHOUSE", "MULTI_FAMILY"]
            property_type1 = ["SingleFamily", "Condo", "Townhouse", "MultiFamily"]
            property_type_mapping = dict(zip(property_type0, property_type1))

            rent_res = api.rent_estimate(property_type_mapping[property_type], address, beds, baths)
            self.rent_data = rent_res.json()
        return self.rent_data

    def get_user_finance_assumptions(self):
        with open(self.user_finance_filepath, 'r') as f:
            self.user_finance = json.load(f)
        return self.user_finance

    
class DataPrep:

    def __init__(self, zpid):
        self.zpid = zpid
        self.user_assumptions = None
        self.amortization = None

    def get_assumptions(self):
        user_assumptions = {}
        assumptions = InvestmentAssumptions()
        cash_reserve = assumptions.get_user_finance_assumptions(self.zpid)['extra_cash_reserves']
        equity_pct = assumptions.get_user_finance_assumptions(self.zpid)['eqt_pct']
        amort_period = assumptions.get_user_finance_assumptions(self.zpid)['amort_period']
        int_rate = assumptions.get_user_finance_assumptions(self.zpid)['int_rate_on_debt']
        price = assumptions.get_listing_price(self.zpid)
        rent = assumptions.get_rent_estimate(self.zpid)['rent']
        insurance = assumptions.get_insurance(self.zpid)
        tax_rate = assumptions.get_tax_rate(self.zpid)['tax_rate']
        if assumptions.closing_costs_ == None:
            closing_costs = np.round(0.015*price, 0)
        else:
            closing_costs = assumptions.closing_costs_
        total_project_cost = price + closing_costs + assumptions.renovation_costs + assumptions.exit_renovation_cost
        user_assumptions['monthly_gross_rent'] = rent
        user_assumptions['purchase_price'] = price
        user_assumptions['purchase_date'] = datetime.now().strftime('%Y-%m-%d')
        user_assumptions['closing_costs_'] = closing_costs
        user_assumptions['extra_cash_reserves'] = cash_reserve
        user_assumptions['renovation_costs'] = assumptions.renovation_costs
        user_assumptions['renovation_period'] = assumptions.renovation_period
        user_assumptions['exit_renovation_cost'] = assumptions.exit_renovation_cost
        user_assumptions['total_project_cost'] = total_project_cost
        user_assumptions['equity_pct'] = equity_pct
        user_assumptions['total_equity_investment'] = np.round(equity_pct*total_project_cost, 0)
        user_assumptions['total_project_loan_amount'] = np.round((1-equity_pct)*total_project_cost, 0)
        user_assumptions['amortization_period'] = amort_period
        user_assumptions['interest_rate_on_debt'] = int_rate
        user_assumptions['MAX_HOLD'] = assumptions.MAX_HOLD
        user_assumptions['length_of_hold'] = assumptions.length_of_hold
        user_assumptions['appreciation'] = assumptions.appreciation
        user_assumptions['sales_price_at_exit'] = np.round((price*(1+assumptions.appreciation))**min(assumptions.MAX_HOLD, assumptions.length_of_hold), 0)
        user_assumptions['cost_of_sale'] = assumptions.cost_of_sale
        user_assumptions['vacancy_rate'] = assumptions.vacancy_rate
        user_assumptions['rent_growth_rate'] = assumptions.rent_growth_rate
        user_assumptions['repair_allowance'] = assumptions.repair_allowance
        user_assumptions['repair_allowance_amount'] = np.round(assumptions.repair_allowance*rent*12, 0)
        user_assumptions['property_taxes'] = np.round(price*tax_rate, 0)
        user_assumptions['insurance'] = insurance
        user_assumptions['property_manager_rate'] = assumptions.property_manager_rate
        user_assumptions['property_manager_amount'] = np.round(assumptions.property_manager_rate*rent, 0)
        user_assumptions['utilities'] = assumptions.utilities
        user_assumptions['discount_rate'] = assumptions.discount_rate
        self.user_assumptions = user_assumptions
        return user_assumptions

    def get_amortization(self):
        amortization = {}
        if self.user_assumptions is None:
            self.get_assumptions()
        params = self.user_assumptions
        amortization['dates'] = pd.date_range(start=params['purchase_date'], periods=int(12*params['length_of_hold']), freq='M').strftime('%Y-%m-%d').tolist()
        amortization['month_numbers'] = [datetime.strptime(d, '%Y-%m-%d').month for d in amortization['dates']]
        amortization['months'] = [i+1 for i in range(len(amortization['months_numbers']))]
        amortization['rate_per_period'] = (1 + params['interest_rate_on_debt']/12)**(12/12) - 1
        amortization['number_of_payments'] = params['amortization_period']*12
        amortization['monthly_payment'] = -np.round(npf.pmt(rate= params['interest_rate_on_debt']/ 12, nper=params['amortization_period'] * 12, pv=params['total_project_loan_amount'], fv=0, when='end'), 2)
        amortization['amortization_date'] = pd.date_range(start=params['purchase_date'], periods=int(12*params['amortization_period']), freq='M').strftime('%Y-%m-%d').tolist()
        amortization['payment_no'] = [i+1 for i in range(len(amortization['amortization_date']))]
        amortization['amortization_month'] = [i+1 if i <= len(amortization['months'])-1 else 0 for i in range(len(amortization['amortization_date']))]
        amortization['amortization_interest'] = []
        amortization['amortization_balance'] = []
        amortization['amortization_principal'] = []
        amortization['amortization_additional_payment'] = []
        for i in range(len(amortization['amortization_date'])):
            if i == 0:
                amortization['amortization_interest'].append(0)
                amortization['amortization_balance'].append(params['total_project_loan_amount'])
                amortization['amortization_principal'].append(0)
                amortization['amortization_additional_payment'].append(0)
            else:
                amortization['amortization_interest'].append(np.round(amortization['amortization_balance'][i-1]*amortization['rate_per_period'], 2))
                amortization['amortization_principal'].append(np.round(amortization['monthly_payment'] - amortization['amortization_interest'][i], 2))
                amortization['amortization_additional_payment'].append(0)
                amortization['amortization_balance'].append(np.round(amortization['amortization_balance'][i-1] - amortization['amortization_principal'][i] - amortization['amortization_additional_payment'][i], 2))
        self.amortization = amortization
        return amortization

