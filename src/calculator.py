import numpy as np
import pandas as pd
from utils import DataPrep, InvestmentAssumptions
from metrics import Metrics


# Given the assumptions and zpid, return the metrics
zpid = 26834283

dp = DataPrep(zpid)
cash_flow_unleveraged = dp.get_cashflow()['cash_flow_unleveraged']
cash_flow_leveraged = dp.get_cashflow()['cash_flow_leveraged']
dates = dp.get_cashflow()['dates']
dates_xirr = Metrics.xirr_dates(dates)

irr_unleveraged = np.round((Metrics.xirr(values=cash_flow_unleveraged, dates=dates_xirr))*100, 2)
irr_leveraged = np.round((Metrics.xirr(values=cash_flow_leveraged, dates=dates_xirr))*100, 2)
print('IRR (unleveraged):', irr_unleveraged)
print('IRR (leveraged):', irr_leveraged)

# Refine the assumptions for a given zpid, return the metrics
investment_assumptions = InvestmentAssumptions()
investment_assumptions.renovation_costs = 4000
# like that you continue to update assumption values
# then, calculate the metrics as above.



# Cap Rate
Metrics.cap_rate(cash_flow['net_rents'], ua['purchase_price'])

# cash on cash return
Metrics.cash_on_cash_return(cash_flow['net_rents'], cash_flow['less_taxes'], cash_flow['cash_invested'])