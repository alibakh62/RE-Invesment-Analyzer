import os
import sys
sys.path.insert(0, '.')
sys.path.insert(0, '..')

import pickle
import numpy as np
import pandas as pd
import numpy_financial as npf
from datetime import datetime
from src.config import *
import src.api as api
from src.metrics import Metrics

from scipy.optimize import anderson
import json

import logging

# logdatetime = time.strftime("%m%d%Y_%H%M%S")
logdatetime = time.strftime("%m%d%Y")
logging.basicConfig(level=logging.INFO, 
		    format='%(asctime)s %(message)s', 
		    datefmt='%m/%d/%Y %I:%M:%S %p', 
		    filename= f"{LOG_DIR}/{LOG_PROP_DETAILS}_{logdatetime}.log", 
		    filemode='w',
		    force=True)


class InvestmentAssumptions:

    def __init__(self, modify_assumptions=False):
        self.modify_assumptions = modify_assumptions
        self.search_filepath = os.path.join(BASE_DIR, PROP_SEARCH)
        self.user_finance_filepath = os.path.join(BASE_DIR, USER_FINANCE)
        self.user_finance = None
        self.property_details = None
        self.rent_data = None
        self.search_data = None
        self.closing_costs_ = None
        # user assumptions
        self.equity_pct = None
        self.extra_cash_reserves = None
        self.amort_period = None
        self.int_rate_on_debt = None
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
	

    # def set_renovation_assumptions(self, renovation_costs, renovation_period, exit_renovation_cost):
    #     self.renovation_costs = renovation_costs
    #     self.renovation_period = renovation_period
    #     self.exit_renovation_cost = exit_renovation_cost

    # def set_exit_assumptions(self, MAX_HOLD, length_of_hold, appreciation, cost_of_sale):
    #     self.MAX_HOLD = MAX_HOLD
    #     self.length_of_hold = length_of_hold
    #     self.appreciation = appreciation
    #     self.cost_of_sale = cost_of_sale

    # def set_other_assumptions(self, closing_costs_, vacancy_rate, rent_growth_rate, repair_allowance, property_manager_rate, utilities, discount_rate):
    #     self.vacancy_rate = vacancy_rate
    #     self.rent_growth_rate = rent_growth_rate
    #     self.repair_allowance = repair_allowance
    #     self.property_manager_rate = property_manager_rate
    #     self.utilities = utilities
    #     self.discount_rate = discount_rate
    #     self.closing_costs_ = closing_costs_

    def get_property_type(self, zpid):
        if self.property_details is None:
            self.property_details = api.property_detail(zpid).json()
        return self.property_details['propertyTypeDimension']

    def get_property_address(self, zpid):
        if self.property_details is None:
            self.property_details = api.property_detail(zpid).json()
        address = self.property_details['address']
        return address['streetAddress'] + ", " + address['city'] + ", " + address['state'] + " " + address['zipcode']

    def get_no_bedrooms(self, zpid):
        if self.property_details is None:
            self.property_details = api.property_detail(zpid).json()
        return self.property_details['resoFacts']['bedrooms']

    def get_no_bathrooms(self, zpid):
        if self.property_details is None:
            self.property_details = api.property_detail(zpid).json()
        return self.property_details['resoFacts']['bathrooms']

    def get_listing_price(self, zpid):
        if self.property_details is None:
            self.property_details = api.property_detail(zpid).json()
        return self.property_details['price']

    def get_tax_rate(self, zpid):
        tax_info = {}
        if self.property_details is None:
            self.property_details = api.property_detail(zpid).json()
        tax_info['tax_rate'] = self.property_details['propertyTaxRate']
        tax_info['tax_history'] = self.property_details['taxHistory']
        return tax_info

    def get_insurance(self, zpid):
        if self.property_details is None:
            self.property_details = api.property_detail(zpid).json()
        return self.property_details['annualHomeownersInsurance']

    def get_rent_estimate(self, zpid):
        if self.rent_data is None:
            property_type = self.get_property_type(zpid)
            address = self.get_property_address(zpid)
            beds = self.get_no_bedrooms(zpid)
            baths = self.get_no_bathrooms(zpid)
            # creating a mapping between standard property types across different APIs
            property_type0 = ["Single Family", "Condo", "Townhouse", "Multi Family"]
            property_type1 = ["SingleFamily", "Condo", "Townhouse", "MultiFamily"]
            property_type_mapping = dict(zip(property_type0, property_type1))
            rent_res = api.rent_estimate(property_type_mapping[property_type], address, beds, baths)
            self.rent_data = rent_res.json()
        return self.rent_data

    def get_user_finance_assumptions(self):
        with open(self.user_finance_filepath, 'r') as f:
            user_finance_ = json.load(f)
        if self.modify_assumptions:
            self.user_finance = {
                'eqt_pct': user_finance_['eqt_pct'] if self.equity_pct is None else self.equity_pct,
                'extra_cash_reserves': user_finance_['extra_cash_reserves'] if self.extra_cash_reserves is None else self.extra_cash_reserves,
                'amort_period': user_finance_['amort_period'] if self.amort_period is None else self.amort_period,
                'int_rate_on_debt': user_finance_['int_rate_on_debt'] if self.int_rate_on_debt is None else self.int_rate_on_debt
            }
        else:
            self.user_finance = user_finance_
        return self.user_finance

    
class DataPrep:

    def __init__(self, zpid, investment_assumptions=None):
        self.zpid = zpid
        self.user_assumptions = None
        self.amortization = None
        self.cash_flow = None
        self.prop_detail = None  #TODO: every time called try to read from file, if not, call api
        self.investment_assumptions = investment_assumptions

    def np_encoder(self, object):
        if isinstance(object, np.generic):
            return object.item()

    @classmethod
    def cumulative(cls, lists):
        cu_list = []
        length = len(lists)
        cu_list = [sum(lists[0:x:1]) for x in range(0, length+1)]
        return np.sum(cu_list[1:])

    @classmethod
    def calc_rent_cash_flow(cls, months, monthly_gross_rent, rental_growth_rate, lease_up, exit_sale, project_life):
        rent_cash_flow = []
        rent_cash_flow.append(lease_up[0]*monthly_gross_rent)
        for i in range(1, len(months)):
            rent_cash_flow.append(int(np.round(max(lease_up[i]*monthly_gross_rent*(1+rental_growth_rate[i]), (rent_cash_flow[i-1]*(1+rental_growth_rate[i])))*project_life[i], 0)))
        return rent_cash_flow

    def get_assumptions(self):
        user_assumptions = {}
        if self.investment_assumptions is None:
            self.investment_assumptions = InvestmentAssumptions()
        assumptions = self.investment_assumptions
        cash_reserve = assumptions.get_user_finance_assumptions()['extra_cash_reserves']
        equity_pct = assumptions.get_user_finance_assumptions()['eqt_pct']
        amort_period = assumptions.get_user_finance_assumptions()['amort_period']
        int_rate = assumptions.get_user_finance_assumptions()['int_rate_on_debt']
        price = assumptions.get_listing_price(self.zpid)
        try:
            # print(assumptions.get_rent_estimate(self.zpid))
            rent = assumptions.get_rent_estimate(self.zpid)['rent']
        except KeyError:
            rent = assumptions.get_rent_estimate(self.zpid)['median']
        insurance = assumptions.get_insurance(self.zpid)
        tax_rate = assumptions.get_tax_rate(self.zpid)['tax_rate']
        self.prop_detail = assumptions.property_details
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
        user_assumptions['sales_price_at_exit'] = np.round(price*(1+assumptions.appreciation)**min(assumptions.MAX_HOLD, assumptions.length_of_hold), 0)
        user_assumptions['cost_of_sale'] = assumptions.cost_of_sale
        user_assumptions['vacancy_rate'] = assumptions.vacancy_rate
        user_assumptions['rent_growth_rate'] = assumptions.rent_growth_rate
        user_assumptions['repair_allowance'] = assumptions.repair_allowance
        user_assumptions['repair_allowance_amount'] = np.round(assumptions.repair_allowance*rent*12, 0)
        user_assumptions['property_taxes'] = np.round(price*tax_rate*0.01, 0)
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
        amortization['months'] = [i+1 for i in range(len(amortization['month_numbers']))]
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

    def get_cashflow(self):
        logging.info(f'Getting cashflow for {self.zpid}')
        cash_flow = {}
        if self.user_assumptions is None:
            self.get_assumptions()
        if self.amortization is None:
            self.get_amortization()
        params = self.user_assumptions
        amort = self.amortization
        cash_flow['dates'] = amort['dates']
        cash_flow['month_numbers'] = amort['month_numbers']
        cash_flow['months'] = amort['months']
        cash_flow['lease_up'] = [0 if cash_flow['months'][i] <= params['renovation_period'] else 1 for i in range(len(cash_flow['months']))]
        cash_flow['exit_sale'] = [0 if np.round(min(min(np.round(params['length_of_hold'], 0), 7), 7), 0)*12 != cash_flow['months'][i] else 1 for i in range(len(cash_flow['months']))]
        cash_flow['project_life'] = [0 if self.cumulative(cash_flow['exit_sale'][:i]) == 1 else 1 for i in range(len(cash_flow['exit_sale']))]
        # rent assumptions
        cash_flow['rental_growth_rate'] = [params['rent_growth_rate'] if (cash_flow['months'][i] % 12) == 0 else 0 for i in range(len(cash_flow['months']))]
        cash_flow['vacancy'] = [params['vacancy_rate'] for i in range(len(cash_flow['months']))]
        # project costs
        cash_flow['closing_costs'] = [0 for i in range(len(cash_flow['months']))]
        cash_flow['closing_costs'][0] = -params['closing_costs_']
        cash_flow['purchase_costs'] = [0 for i in range(len(cash_flow['months']))]
        cash_flow['purchase_costs'][0] = -params['purchase_price']
        renovations0 = [-params['renovation_costs']//params['renovation_period'] if cash_flow['months'][i] <= params['renovation_period'] else 0 for i in range(len(cash_flow['months']))]
        renovations1 = [params['exit_renovation_cost'] if cash_flow['months'][i] == min(params['length_of_hold'], params['MAX_HOLD'])*12 else 0 for i in range(len(cash_flow['months']))]
        cash_flow['renovations'] = [renovations0[i]-renovations1[i] for i in range(len(cash_flow['months']))]
        cash_flow['total_project_costs'] = [cash_flow['closing_costs'][i]+cash_flow['purchase_costs'][i]+cash_flow['renovations'][i] for i in range(len(cash_flow['months']))]
        # Net rent
        cash_flow['cash_invested'] = [0 for i in range(len(cash_flow['months']))]
        cash_flow['cash_invested'][0] = params['total_equity_investment']
        cash_flow['extra_reserves'] = [0 for i in range(len(cash_flow['months']))]
        cash_flow['extra_reserves'][0] = params['extra_cash_reserves']
        cash_flow['rents'] = self.calc_rent_cash_flow(cash_flow['months'], params['monthly_gross_rent'], cash_flow['rental_growth_rate'], cash_flow['lease_up'], cash_flow['exit_sale'], cash_flow['project_life'])
        cash_flow['less_vacancy'] = [params['vacancy_rate']*cash_flow['rents'][i] for i in range(len(cash_flow['months']))]
        cash_flow['less_management_fees'] = [params['property_manager_rate']*cash_flow['rents'][i] for i in range(len(cash_flow['months']))]
        cash_flow['less_repairs'] = [params['repair_allowance']*cash_flow['rents'][i] for i in range(len(cash_flow['months']))]
        cash_flow['less_taxes'] = [params['property_taxes']*cash_flow['project_life'][i] if i % 12 == 0 else 0 for i in range(len(cash_flow['months']))]
        cash_flow['less_insurance'] = [params['insurance']*cash_flow['project_life'][i] if i % 12 == 0 else 0 for i in range(len(cash_flow['months']))]
        cash_flow['less_utilities'] = [cash_flow['lease_up'][i]*cash_flow['project_life'][i]*params['utilities'] for i in range(len(cash_flow['months']))]
        cash_flow['net_rents'] = [np.round(cash_flow['rents'][i]-cash_flow['less_management_fees'][i]-cash_flow['less_vacancy'][i]-cash_flow['less_repairs'][i]-cash_flow['less_taxes'][i]-cash_flow['less_insurance'][i]-cash_flow['less_utilities'][i], 0) for i in range(len(cash_flow['months']))]
        # Loan principal
        cash_flow['interest'] = [np.round(amort['amortization_interest'][i+1], 0) for i in range(len(cash_flow['months']))]
        cash_flow['interest_paid_from_rents'] = [max(0, min(cash_flow['net_rents'][i], cash_flow['interest'][i])) for i in range(len(cash_flow['months']))]
        cash_flow['interest_paid_from_account'] = [cash_flow['interest'][i]-cash_flow['interest_paid_from_rents'][i] if cash_flow['net_rents'][i] < cash_flow['interest'][i] else 0 for i in range(len(cash_flow['months']))]
        cash_flow['principal_amount'] = [np.round(amort['amortization_principal'][i+1], 0) for i in range(len(cash_flow['months']))]
        cash_flow['principal_paid_from_rents'] = [max(0, min(cash_flow['principal_amount'][i], cash_flow['net_rents'][i]-cash_flow['interest_paid_from_rents'][i])) for i in range(len(cash_flow['months']))]
        cash_flow['principal_paid_from_account'] = [cash_flow['principal_amount'][i]-cash_flow['principal_paid_from_rents'][i] if cash_flow['principal_amount'][i] > cash_flow['principal_paid_from_rents'][i] else 0 for i in range(len(cash_flow['months']))]
        cash_flow['principal_paid_from_sale'] = [0 for i in range(len(cash_flow['months']))]
        cash_flow['loan_principal'] = []
        for i in range(len(cash_flow['months'])):
            if i == 0:
                cash_flow['loan_principal'].append(params['total_project_loan_amount'])
            else:
                cash_flow['loan_principal'].append(np.round(max(0, cash_flow['loan_principal'][i-1] + cash_flow['interest'][i-1] - cash_flow['interest_paid_from_rents'][i-1] - cash_flow['interest_paid_from_account'][i-1]- cash_flow['principal_paid_from_rents'][i-1] - cash_flow['principal_paid_from_account'][i-1] - cash_flow['principal_paid_from_sale'][i-1]), 0))
        cash_flow['net_rent_debt_services'] = [cash_flow['net_rents'][i]-cash_flow['interest_paid_from_rents'][i]-cash_flow['principal_paid_from_rents'][i] for i in range(len(cash_flow['months']))]
        # Net rents - debt services
        cash_flow['debt_services_paid'] = []
        cash_flow['less_reserves'] = []
        cash_flow['net_rent_deposits'] = []
        cash_flow['bank_account'] = []
        for i in range(len(cash_flow['months'])):
            if i == 0:
                cash_flow['bank_account'].append(cash_flow['cash_invested'][i] + cash_flow['extra_reserves'][i] + cash_flow['net_rents'][i])
                cash_flow['debt_services_paid'].append(min(cash_flow['bank_account'][i], cash_flow['interest_paid_from_account'][i] + cash_flow['principal_paid_from_account'][i]))
                cash_flow['less_reserves'].append(min(0, cash_flow['net_rents'][i] + cash_flow['total_project_costs'][i] + cash_flow['loan_principal'][i]))
                cash_flow['net_rent_deposits'].append(max(0, cash_flow['net_rent_debt_services'][i]))
            else:
                cash_flow['bank_account'].append(cash_flow['bank_account'][i-1] - cash_flow['debt_services_paid'][i-1] + cash_flow['less_reserves'][i-1] + cash_flow['net_rent_deposits'][i-1])
                cash_flow['debt_services_paid'].append(min(cash_flow['bank_account'][i], cash_flow['interest_paid_from_account'][i] + cash_flow['principal_paid_from_account'][i]))
                cash_flow['less_reserves'].append(min(0, cash_flow['net_rents'][i] + cash_flow['total_project_costs'][i]))
                cash_flow['net_rent_deposits'].append(max(0, cash_flow['net_rent_debt_services'][i] - cash_flow['principal_paid_from_account'][i] - cash_flow['interest_paid_from_account'][i]))
        cash_flow['sales_price'] = [0 for i in range(len(cash_flow['months']))]
        cash_flow['sales_price'][-1] = params['sales_price_at_exit']
        cash_flow['less_cost_of_sales'] = [params['cost_of_sale']*cash_flow['sales_price'][i] for i in range(len(cash_flow['months']))]
        cash_flow['less_debt'] = [min(cash_flow['sales_price'][i]-cash_flow['less_cost_of_sales'][i], cash_flow['loan_principal'][i]+cash_flow['interest'][i]-cash_flow['interest_paid_from_rents'][i]-cash_flow['principal_paid_from_rents'][i]) for i in range(len(cash_flow['months']))]
        cash_flow['net_proceeds'] = [np.round(cash_flow['sales_price'][i]-cash_flow['less_cost_of_sales'][i]-cash_flow['less_debt'][i], 0) for i in range(len(cash_flow['months']))]
        cash_flow['cash_flow_unleveraged'] = []
        cash_flow['cash_flow_leveraged'] = []
        for i in range(len(cash_flow['months'])):
            if i == 0:
                cash_flow['cash_flow_unleveraged'].append(cash_flow['total_project_costs'][i]+cash_flow['extra_reserves'][i]+cash_flow['net_rents'][i]+cash_flow['sales_price'][i]-cash_flow['less_cost_of_sales'][i])
                if params['equity_pct'] == 1:
                    unlevered_amt = cash_flow['cash_flow_unleveraged'][i]
                else:
                    unlevered_amt = -cash_flow['cash_invested'][i] + cash_flow['net_rents'][i] - cash_flow['extra_reserves'][i]
                cash_flow['cash_flow_leveraged'].append(unlevered_amt)
            else:
                cash_flow['cash_flow_unleveraged'].append(cash_flow['total_project_costs'][i]+cash_flow['net_rents'][i]+cash_flow['sales_price'][i]-cash_flow['less_cost_of_sales'][i])
                if params['equity_pct'] == 1:
                    unlevered_amt = cash_flow['cash_flow_unleveraged'][i]
                else:
                    unlevered_amt = cash_flow['net_rent_debt_services'][i] + cash_flow['net_proceeds'][i]
                cash_flow['cash_flow_leveraged'].append(unlevered_amt)
        self.cash_flow = cash_flow
        with open(os.path.join(BASE_DIR, USER_ASSUMPTIONS), 'wb') as f:
            pickle.dump(self.user_assumptions, f)
        with open(os.path.join(BASE_DIR, CASH_FLOW), 'wb') as f:
            pickle.dump(self.cash_flow, f)
        with open(os.path.join(BASE_DIR, AMORTIZATION), 'wb') as f:
            pickle.dump(self.amortization, f)
        return cash_flow

    def get_metrics(self):
        cash_flow = self.get_cashflow()
        price = self.prop_detail['price']
        cash_flow_unleveraged = cash_flow['cash_flow_unleveraged']
        cash_flow_leveraged = cash_flow['cash_flow_leveraged']
        dates = cash_flow['dates']
        dates_xirr = Metrics.xirr_dates(dates)
        irr_unleveraged = np.round((Metrics.xirr(values=cash_flow_unleveraged, dates=dates_xirr))*100, 2)
        irr_leveraged = np.round((Metrics.xirr(values=cash_flow_leveraged, dates=dates_xirr))*100, 2)
        cap_rate = Metrics.cap_rate(cash_flow['net_rents'], price)
        coc = Metrics.cash_on_cash_return(cash_flow['net_rents'], cash_flow['less_taxes'], cash_flow['cash_invested'])
        return irr_unleveraged, irr_leveraged, cap_rate, coc

