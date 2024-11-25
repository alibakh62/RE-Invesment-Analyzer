"""Financial calculations and metrics utilities."""
from typing import List, Dict, Optional
import numpy_financial as npf
import pandas as pd

def calculate_mortgage_payment(principal: float, rate: float, years: int) -> float:
    """Calculate monthly mortgage payment."""
    monthly_rate = rate / 12
    num_payments = years * 12
    return -npf.pmt(monthly_rate, num_payments, principal)

def calculate_amortization_schedule(principal: float, rate: float, years: int) -> pd.DataFrame:
    """Generate amortization schedule."""
    monthly_rate = rate / 12
    num_payments = years * 12
    payment = calculate_mortgage_payment(principal, rate, years)
    
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
            'Balance': balance
        })
    
    return pd.DataFrame(schedule)

def calculate_cash_flow_metrics(cash_flows: List[float], rate: float) -> Dict[str, float]:
    """Calculate investment metrics from cash flows."""
    try:
        irr = npf.irr(cash_flows)
        npv = npf.npv(rate, cash_flows)
        
        # Cash on Cash return (first year cash flow / initial investment)
        coc_return = (cash_flows[1] / -cash_flows[0]) * 100 if len(cash_flows) > 1 else 0
        
        return {
            'IRR': irr,
            'NPV': npv,
            'Cash_on_Cash': coc_return
        }
    except Exception as e:
        print(f"Error calculating metrics: {str(e)}")
        return {
            'IRR': 0.0,
            'NPV': 0.0,
            'Cash_on_Cash': 0.0
        }

def calculate_operating_expenses(
    effective_gross_income: float,
    vacancy_rate: float = 0.05,
    management_fee_rate: float = 0.10,
    maintenance_rate: float = 0.05,
    property_tax_rate: float = 0.02,
    insurance_rate: float = 0.005
) -> Dict[str, float]:
    """Calculate annual operating expenses."""
    vacancy_loss = effective_gross_income * vacancy_rate
    management_fees = effective_gross_income * management_fee_rate
    maintenance = effective_gross_income * maintenance_rate
    property_tax = effective_gross_income * property_tax_rate
    insurance = effective_gross_income * insurance_rate
    
    total_expenses = vacancy_loss + management_fees + maintenance + property_tax + insurance
    
    return {
        'Vacancy_Loss': vacancy_loss,
        'Management_Fees': management_fees,
        'Maintenance': maintenance,
        'Property_Tax': property_tax,
        'Insurance': insurance,
        'Total_Expenses': total_expenses
    }

def calculate_roi_metrics(
    purchase_price: float,
    down_payment_pct: float,
    annual_rent: float,
    annual_expenses: float,
    mortgage_payment: float,
    appreciation_rate: float = 0.03,
    holding_period: int = 5
) -> Dict[str, float]:
    """Calculate ROI metrics for an investment property."""
    down_payment = purchase_price * (down_payment_pct / 100)
    loan_amount = purchase_price - down_payment
    
    # Annual cash flow
    annual_cash_flow = annual_rent - annual_expenses - (mortgage_payment * 12)
    
    # Future property value
    future_value = purchase_price * (1 + appreciation_rate) ** holding_period
    
    # Remaining loan balance after holding period
    remaining_balance = loan_amount * (1 - (down_payment_pct / 100)) ** holding_period
    
    # Total profit
    total_profit = (future_value - remaining_balance - purchase_price) + \
                  (annual_cash_flow * holding_period)
    
    # ROI
    roi = (total_profit / down_payment) * 100
    
    # Cap rate
    noi = annual_rent - annual_expenses
    cap_rate = (noi / purchase_price) * 100
    
    return {
        'Annual_Cash_Flow': annual_cash_flow,
        'Total_Profit': total_profit,
        'ROI': roi,
        'Cap_Rate': cap_rate,
        'Future_Value': future_value
    }
