"""Financial calculations and metrics utilities."""
from typing import List, Dict, Optional, Union, Tuple
import numpy as np
import pandas as pd
import numpy_financial as npf
from datetime import datetime, date
from dataclasses import dataclass

@dataclass
class FinancialMetrics:
    """Container for financial metrics."""
    irr: float
    npv: float
    cap_rate: float
    cash_on_cash: float
    debt_service_coverage: float
    roi: float
    total_return: float
    equity_multiple: float

class FinancialCalculator:
    """Financial calculations for real estate investments."""
    
    @staticmethod
    def calculate_mortgage_payment(principal: float, rate: float, years: int) -> float:
        """Calculate monthly mortgage payment."""
        monthly_rate = rate / 12 / 100  # Convert annual rate to monthly decimal
        num_payments = years * 12
        return -npf.pmt(monthly_rate, num_payments, principal)
    
    @staticmethod
    def calculate_amortization_schedule(
        principal: float,
        rate: float,
        years: int
    ) -> pd.DataFrame:
        """Generate amortization schedule."""
        monthly_rate = rate / 12 / 100
        num_payments = years * 12
        payment = FinancialCalculator.calculate_mortgage_payment(principal, rate, years)
        
        schedule = []
        balance = principal
        
        for period in range(1, num_payments + 1):
            interest = balance * monthly_rate
            principal_paid = payment - interest
            balance -= principal_paid
            
            schedule.append({
                'Period': period,
                'Payment': payment,
                'Principal': principal_paid,
                'Interest': interest,
                'Balance': max(0, balance)  # Ensure balance doesn't go below 0
            })
        
        return pd.DataFrame(schedule)
    
    @staticmethod
    def calculate_cash_flows(
        purchase_price: float,
        monthly_rent: float,
        operating_expenses: float,
        mortgage_payment: float,
        holding_period: int = 5,
        down_payment_pct: float = 20,
        closing_cost_pct: float = 2,
        selling_cost_pct: float = 6,
        appreciation_rate: float = 3,
        rent_growth_rate: float = 2,
        expense_growth_rate: float = 2,
        renovation_cost: float = 0,
        extra_reserves: float = 0
    ) -> pd.DataFrame:
        """Calculate projected cash flows."""
        # Initial investment
        down_payment = purchase_price * (down_payment_pct / 100)
        closing_costs = purchase_price * (closing_cost_pct / 100)
        total_initial_investment = down_payment + closing_costs + renovation_cost + extra_reserves
        
        cash_flows = []
        
        # Initial investment (Year 0)
        cash_flows.append({
            'Year': 0,
            'Rental_Income': 0,
            'Operating_Expenses': 0,
            'Mortgage_Payment': 0,
            'Net_Operating_Income': 0,
            'Property_Value': purchase_price,
            'Cash_Flow': -total_initial_investment
        })
        
        # Projected cash flows for each year
        for year in range(1, holding_period + 1):
            # Calculate income and expenses with growth
            annual_rent = monthly_rent * 12 * ((1 + rent_growth_rate/100) ** year)
            annual_expenses = operating_expenses * ((1 + expense_growth_rate/100) ** year)
            annual_mortgage = mortgage_payment * 12
            
            # Calculate property value
            property_value = purchase_price * ((1 + appreciation_rate/100) ** year)
            
            # Net operating income
            noi = annual_rent - annual_expenses
            
            # Cash flow before sales proceeds
            cash_flow = noi - annual_mortgage
            
            # Add sales proceeds in final year
            if year == holding_period:
                selling_costs = property_value * (selling_cost_pct / 100)
                loan_balance = FinancialCalculator.calculate_loan_balance(
                    principal=purchase_price * (1 - down_payment_pct/100),
                    rate=rate,
                    years=30,  # Assuming 30-year mortgage
                    payments_made=year * 12
                )
                net_sales_proceeds = property_value - selling_costs - loan_balance
                cash_flow += net_sales_proceeds
            
            cash_flows.append({
                'Year': year,
                'Rental_Income': annual_rent,
                'Operating_Expenses': annual_expenses,
                'Mortgage_Payment': annual_mortgage,
                'Net_Operating_Income': noi,
                'Property_Value': property_value,
                'Cash_Flow': cash_flow
            })
        
        return pd.DataFrame(cash_flows)
    
    @staticmethod
    def calculate_loan_balance(
        principal: float,
        rate: float,
        years: int,
        payments_made: int
    ) -> float:
        """Calculate remaining loan balance after a number of payments."""
        monthly_rate = rate / 12 / 100
        num_payments = years * 12
        payment = FinancialCalculator.calculate_mortgage_payment(principal, rate, years)
        
        return -npf.fv(
            monthly_rate,
            payments_made,
            payment,
            principal,
            when='end'
        )
    
    @staticmethod
    def calculate_metrics(
        cash_flows: pd.DataFrame,
        purchase_price: float,
        discount_rate: float = 8
    ) -> FinancialMetrics:
        """Calculate investment metrics from cash flows."""
        try:
            # Extract cash flow values
            values = cash_flows['Cash_Flow'].values
            
            # Calculate IRR
            irr = np.irr(values) * 100
            
            # Calculate NPV
            npv = npf.npv(discount_rate/100, values)
            
            # Calculate Cap Rate (NOI / Purchase Price)
            first_year_noi = cash_flows.loc[1, 'Net_Operating_Income']
            cap_rate = (first_year_noi / purchase_price) * 100
            
            # Cash on Cash Return (First year cash flow / Initial investment)
            initial_investment = -values[0]
            first_year_cf = values[1]
            cash_on_cash = (first_year_cf / initial_investment) * 100
            
            # Debt Service Coverage Ratio
            first_year_mortgage = cash_flows.loc[1, 'Mortgage_Payment']
            debt_service_coverage = first_year_noi / first_year_mortgage
            
            # ROI
            total_profit = sum(values[1:])  # Exclude initial investment
            roi = (total_profit / initial_investment) * 100
            
            # Total Return
            total_return = total_profit
            
            # Equity Multiple
            equity_multiple = (initial_investment + total_profit) / initial_investment
            
            return FinancialMetrics(
                irr=irr,
                npv=npv,
                cap_rate=cap_rate,
                cash_on_cash=cash_on_cash,
                debt_service_coverage=debt_service_coverage,
                roi=roi,
                total_return=total_return,
                equity_multiple=equity_multiple
            )
            
        except Exception as e:
            print(f"Error calculating metrics: {str(e)}")
            return FinancialMetrics(
                irr=0.0,
                npv=0.0,
                cap_rate=0.0,
                cash_on_cash=0.0,
                debt_service_coverage=0.0,
                roi=0.0,
                total_return=0.0,
                equity_multiple=0.0
            )
    
    @staticmethod
    def calculate_operating_expenses(
        effective_gross_income: float,
        property_tax_rate: float = 1.2,
        insurance_rate: float = 0.5,
        maintenance_rate: float = 5.0,
        management_rate: float = 8.0,
        utilities_rate: float = 0.0,
        hoa_fees: float = 0.0
    ) -> Dict[str, float]:
        """Calculate annual operating expenses."""
        property_tax = effective_gross_income * (property_tax_rate / 100)
        insurance = effective_gross_income * (insurance_rate / 100)
        maintenance = effective_gross_income * (maintenance_rate / 100)
        management = effective_gross_income * (management_rate / 100)
        utilities = effective_gross_income * (utilities_rate / 100)
        
        total_expenses = sum([
            property_tax,
            insurance,
            maintenance,
            management,
            utilities,
            hoa_fees
        ])
        
        return {
            'Property_Tax': property_tax,
            'Insurance': insurance,
            'Maintenance': maintenance,
            'Property_Management': management,
            'Utilities': utilities,
            'HOA_Fees': hoa_fees,
            'Total_Expenses': total_expenses
        }
