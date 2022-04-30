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