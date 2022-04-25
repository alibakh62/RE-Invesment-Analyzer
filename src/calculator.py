"""
List of metrics:
	- Levered IRR
	- Unlevered IRR
	- Mortgage Payment
	- Total Payments
	- Total Interest
	- Cash Required
	- Minimum Monthly Expenses
	- Monthly Cash Flow
	- Max Purhcase Price
	- Annual Yield (CoC ROI)
	- Cap Rate

It requires the following input data:
	- Purchase Price
	- Rental Income
	- Closing Costs
	- Loan Amount
	- Interest Rate
	- Vacancy Rate
	- Loan Term
	- Maintenance Expense
	- Property Management Fees
	- Annual Property Taxes
	- Annual Property Insurance
"""

# Metric Definitions:
# ===================
# Cash on Cash = (Annual Cash Flow / Actual Cash In) * 100
# Expenses = Mortgage payment + (Annual taxes + Annual Insurance)/12 + 
#            + (Rental Income * Vacancy Rate)
#            + (Rental Income * Maintenance Rate)
#            + (Rental Income * Property Management Fees)
# Cash Flow = Rental Income - Expenses (Monthly Expenses)
# Cap Rate = (Annual Cash Flow / Market Value of Property) * 100
# ==============================================================

import sys
import pandas as pd

def get_mortgate_pmt(principal, irate, term):
    """
    Calculate the monthly mortgage payment from mortgage details
    """
    irate = irate/1200  # -> percentage rate / 12 since monthly payment
    return float(principal) * float((irate*(1+irate)**term) / (((1+irate)**term)-1))


def calc_expenses(rent, vac_rate, maint_rate, prop_mgmt_fees, taxes, insurance):
    """
    returns all non-mortgage payment expenses for a month 
    """
    return (rent * vac_rate) \
              + (rent * maint_rate) \
              + (rent * prop_mgmt_fees) \
              + (taxes / 12) \
              + (insurance / 12)


def calc_cash_flow(rent, vac_rate, maint_rate, prop_mgmt_fees, taxes, insurance, mgt_payment):
    """
    determines the monthly cash flow expected from the property
    """
    expenses = calc_expenses(rent, vac_rate, maint_rate, prop_mgmt_fees, taxes, insurance)
    return rent - expenses - mgt_payment


def calc_max_principal(rent, vac_rate, maint_rate, prop_mgmt_fees, taxes, insurance, \
                       irate, term, min_cf=100):
    """
    Calculate the maximum principal for the property to ensure that the cash flow >= min_cf
    """
    irate = irate/1200
    expenses = calc_expenses(rent, vac_rate, maint_rate, prop_mgmt_fees, taxes, insurance)
    qty = float((irate*(1+irate)**term) / (((1+irate)**term)-1))
    p = (-min_cf + rent - expenses) / qty
    return p/.8


def read_data(filename):
    """
    Reads the data from the csv file
    """
    return pd.read_csv(filename, sep=r'\s*,\s*', encoding='ascii', engine='python')


