"""Data preparation utilities for investment analysis."""
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from dataclasses import dataclass
from datetime import datetime

from src.models.property import PropertyDetails
from src.services.zillow_service import ZillowService
from src.utils.financial import FinancialCalculator, FinancialMetrics
from src.config.settings import DEFAULT_INVESTMENT_ASSUMPTIONS, ANALYSIS_CONFIG

@dataclass
class InvestmentAssumptions:
    """Investment assumptions for analysis."""
    equity_percentage: float = DEFAULT_INVESTMENT_ASSUMPTIONS['equity_percentage']
    interest_rate: float = DEFAULT_INVESTMENT_ASSUMPTIONS['interest_rate']
    amortization_period: int = DEFAULT_INVESTMENT_ASSUMPTIONS['amortization_period']
    renovation_budget: float = DEFAULT_INVESTMENT_ASSUMPTIONS['renovation_budget']
    extra_cash_reserves: float = DEFAULT_INVESTMENT_ASSUMPTIONS['extra_cash_reserves']
    rental_growth_rate: float = DEFAULT_INVESTMENT_ASSUMPTIONS['rental_growth_rate']
    expense_growth_rate: float = DEFAULT_INVESTMENT_ASSUMPTIONS['expense_growth_rate']
    vacancy_rate: float = DEFAULT_INVESTMENT_ASSUMPTIONS['vacancy_rate']
    property_mgmt_rate: float = DEFAULT_INVESTMENT_ASSUMPTIONS['property_mgmt_rate']
    maintenance_rate: float = DEFAULT_INVESTMENT_ASSUMPTIONS['maintenance_rate']
    holding_period: int = ANALYSIS_CONFIG['default_holding_period']
    appreciation_rate: float = ANALYSIS_CONFIG['default_appreciation_rate']

class InvestmentAnalyzer:
    """Analyze investment properties using Zillow data and user assumptions."""
    
    def __init__(
        self,
        zillow_service: ZillowService,
        assumptions: Optional[InvestmentAssumptions] = None
    ):
        self.zillow = zillow_service
        self.assumptions = assumptions or InvestmentAssumptions()
        self.calculator = FinancialCalculator()
    
    def analyze_property(self, property_details: PropertyDetails) -> Dict[str, Any]:
        """Analyze a property and return comprehensive metrics."""
        try:
            # Get rent estimate if not available
            monthly_rent = property_details.rent_estimate
            if not monthly_rent:
                monthly_rent = self.zillow.get_rent_estimate(property_details) or 0
            
            # Calculate loan details
            loan_amount = property_details.price * (1 - self.assumptions.equity_percentage/100)
            monthly_payment = self.calculator.calculate_mortgage_payment(
                principal=loan_amount,
                rate=self.assumptions.interest_rate,
                years=self.assumptions.amortization_period
            )
            
            # Calculate operating expenses
            annual_rent = monthly_rent * 12
            expenses = self.calculator.calculate_operating_expenses(
                effective_gross_income=annual_rent,
                property_tax_rate=ANALYSIS_CONFIG['property_tax_rate'],
                insurance_rate=ANALYSIS_CONFIG['insurance_rate'],
                maintenance_rate=self.assumptions.maintenance_rate,
                management_rate=self.assumptions.property_mgmt_rate
            )
            
            # Calculate cash flows
            cash_flows = self.calculator.calculate_cash_flows(
                purchase_price=property_details.price,
                monthly_rent=monthly_rent,
                operating_expenses=expenses['Total_Expenses'],
                mortgage_payment=monthly_payment,
                holding_period=self.assumptions.holding_period,
                down_payment_pct=self.assumptions.equity_percentage,
                closing_cost_pct=ANALYSIS_CONFIG['closing_cost_rate'],
                appreciation_rate=self.assumptions.appreciation_rate,
                rent_growth_rate=self.assumptions.rental_growth_rate,
                expense_growth_rate=self.assumptions.expense_growth_rate,
                renovation_cost=self.assumptions.renovation_budget,
                extra_reserves=self.assumptions.extra_cash_reserves
            )
            
            # Calculate metrics
            metrics = self.calculator.calculate_metrics(
                cash_flows=cash_flows,
                purchase_price=property_details.price
            )
            
            # Generate amortization schedule
            amortization = self.calculator.calculate_amortization_schedule(
                principal=loan_amount,
                rate=self.assumptions.interest_rate,
                years=self.assumptions.amortization_period
            )
            
            return {
                'property': property_details,
                'assumptions': self.assumptions,
                'monthly_rent': monthly_rent,
                'monthly_mortgage': monthly_payment,
                'operating_expenses': expenses,
                'cash_flows': cash_flows,
                'metrics': metrics,
                'amortization': amortization
            }
            
        except Exception as e:
            print(f"Error analyzing property: {str(e)}")
            return None
    
    def analyze_multiple_properties(
        self,
        properties: List[PropertyDetails]
    ) -> pd.DataFrame:
        """Analyze multiple properties and return comparative metrics."""
        results = []
        
        for prop in properties:
            analysis = self.analyze_property(prop)
            if analysis:
                metrics = analysis['metrics']
                results.append({
                    'Address': prop.address,
                    'Price': prop.price,
                    'Monthly_Rent': analysis['monthly_rent'],
                    'Monthly_Mortgage': analysis['monthly_mortgage'],
                    'Operating_Expenses': analysis['operating_expenses']['Total_Expenses'],
                    'IRR': metrics.irr,
                    'Cap_Rate': metrics.cap_rate,
                    'Cash_on_Cash': metrics.cash_on_cash,
                    'ROI': metrics.roi,
                    'Debt_Service_Coverage': metrics.debt_service_coverage
                })
        
        return pd.DataFrame(results)
    
    def get_top_investments(
        self,
        properties: List[PropertyDetails],
        sort_by: str = 'IRR',
        ascending: bool = False,
        top_n: int = 10
    ) -> pd.DataFrame:
        """Get top N investment properties based on specified metric."""
        df = self.analyze_multiple_properties(properties)
        return df.nlargest(top_n, sort_by) if not ascending else df.nsmallest(top_n, sort_by)
