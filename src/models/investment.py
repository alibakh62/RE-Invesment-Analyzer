from dataclasses import dataclass
from typing import Optional, Dict, List
import numpy_financial as npf
import pandas as pd
import numpy as np
from datetime import datetime

@dataclass
class InvestmentAssumptions:
    equity_percentage: float
    cash_reserves: float
    amortization_period: int
    interest_rate: float
    renovation_budget: Optional[float] = 0.0
    extra_cash_reserves: Optional[float] = 0.0
    rental_growth_rate: Optional[float] = 0.02
    expense_growth_rate: Optional[float] = 0.02
    vacancy_rate: Optional[float] = 0.05
    property_mgmt_rate: Optional[float] = 0.10
    maintenance_rate: Optional[float] = 0.05
    
    def calculate_monthly_payment(self, principal: float) -> float:
        return -npf.pmt(
            rate=self.interest_rate / 12,
            nper=self.amortization_period * 12,
            pv=principal
        )

    def to_dict(self) -> Dict:
        return {
            "equity_percentage": self.equity_percentage,
            "cash_reserves": self.cash_reserves,
            "amortization_period": self.amortization_period,
            "interest_rate": self.interest_rate,
            "renovation_budget": self.renovation_budget,
            "extra_cash_reserves": self.extra_cash_reserves,
            "rental_growth_rate": self.rental_growth_rate,
            "expense_growth_rate": self.expense_growth_rate,
            "vacancy_rate": self.vacancy_rate,
            "property_mgmt_rate": self.property_mgmt_rate,
            "maintenance_rate": self.maintenance_rate
        }

class Investment:
    def __init__(self, property_id: str, assumptions: InvestmentAssumptions):
        self.property_id = property_id
        self.assumptions = assumptions
        
    def calculate_amortization(self, loan_amount: float) -> pd.DataFrame:
        """Calculate loan amortization schedule."""
        periods = self.assumptions.amortization_period * 12
        rate = self.assumptions.interest_rate / 12
        payment = self.assumptions.calculate_monthly_payment(loan_amount)
        
        amort_schedule = []
        balance = loan_amount
        
        for period in range(1, periods + 1):
            interest = balance * rate
            principal = payment - interest
            balance = balance - principal
            
            amort_schedule.append({
                'Period': period,
                'Payment': payment,
                'Principal': principal,
                'Interest': interest,
                'Balance': balance
            })
        
        return pd.DataFrame(amort_schedule)

    def calculate_cash_flows(self, purchase_price: float, monthly_rent: float, 
                           project_life: int = 5) -> pd.DataFrame:
        """Calculate projected cash flows."""
        # Initial investment calculations
        down_payment = purchase_price * (self.assumptions.equity_percentage / 100)
        loan_amount = purchase_price - down_payment
        
        # Monthly calculations
        monthly_payment = self.assumptions.calculate_monthly_payment(loan_amount)
        effective_rent = monthly_rent * (1 - self.assumptions.vacancy_rate)
        property_mgmt = effective_rent * self.assumptions.property_mgmt_rate
        maintenance = effective_rent * self.assumptions.maintenance_rate
        
        cash_flows = []
        for year in range(project_life + 1):
            if year == 0:
                # Initial investment
                cash_flows.append({
                    'Year': year,
                    'Cash Flow': -(down_payment + self.assumptions.renovation_budget + 
                                 self.assumptions.cash_reserves + 
                                 self.assumptions.extra_cash_reserves)
                })
                continue
                
            # Apply growth rates
            current_rent = effective_rent * (1 + self.assumptions.rental_growth_rate) ** year
            current_expenses = (property_mgmt + maintenance) * (1 + self.assumptions.expense_growth_rate) ** year
            
            annual_cash_flow = (current_rent * 12) - (current_expenses * 12) - (monthly_payment * 12)
            
            cash_flows.append({
                'Year': year,
                'Cash Flow': annual_cash_flow
            })
            
        return pd.DataFrame(cash_flows)

    def calculate_metrics(self, purchase_price: float, monthly_rent: float,
                         project_life: int = 5) -> Dict[str, float]:
        """Calculate investment metrics including IRR, NPV, and Cash-on-Cash return."""
        cash_flows_df = self.calculate_cash_flows(purchase_price, monthly_rent, project_life)
        cash_flows = cash_flows_df['Cash Flow'].tolist()
        
        metrics = {
            'IRR': npf.irr(cash_flows),
            'NPV': npf.npv(self.assumptions.interest_rate, cash_flows),
            'Cash_on_Cash': (cash_flows[1] / -cash_flows[0]) * 100  # First year cash flow / Initial investment
        }
        
        return metrics
