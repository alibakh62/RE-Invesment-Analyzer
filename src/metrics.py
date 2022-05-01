import sys
import pandas as pd
import numpy as np
import numpy_financial as npf
from datetime import datetime
from scipy.optimize import anderson


class Metrics:

    def __init__(self):
        pass

    @classmethod
    def xnpv(cls, rate, values, dates):
        
        if rate <= -1.0:
            return float('inf')
        min_date = min(dates)
        return sum([
            value / (1 + rate)**((date - min_date).days / 365)
            for value, date
            in zip(values, dates)
        ])

    @classmethod
    def xirr(cls, values, dates):
        return anderson(lambda r: cls.xnpv(r, values, dates), 0)

    @classmethod
    def xirr_dates(cls, dates):
        return [datetime.strptime(i, '%Y-%m-%d').date() for i in dates]

    @classmethod
    def cap_rate(cls, net_rents, purchase_price):
        """
        cap rate = annual net return / current market value
        """
        return np.round((np.sum(net_rents[:12]) / purchase_price)*100, 2)

    @classmethod
    def cash_on_cash_return(cls, net_rents, taxes, cash_invested):
        """
        CoC = Annual Pre-Tax Cash Flow / Total Cash Invested
        APTCF = (GSR + OI) - (V + OE + AMP)
        GSR = Gross Scheduled Rent
        OI = Other Income
        V = Vacancy
        OE = Operating Expenses
        AMP = Annual Mortgage Payment
        """
        """
        """
        aptcf = np.sum(net_rents[:12]) + np.sum(taxes[:12])
        return np.round((aptcf / np.sum(cash_invested[:12]))*100, 2)