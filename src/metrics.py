import sys
import pandas as pd
import numpy as np
import numpy_financial as npf
from datetime import datetime
from utils import DataPrep


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