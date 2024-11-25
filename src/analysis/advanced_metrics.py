"""Advanced financial metrics for real estate investment analysis."""
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
from dataclasses import dataclass
from scipy import stats

@dataclass
class TaxMetrics:
    """Tax-related investment metrics."""
    depreciation_annual: float
    tax_savings_annual: float
    effective_tax_rate: float
    cost_basis: float
    tax_deductions: Dict[str, float]

@dataclass
class SensitivityMetrics:
    """Sensitivity analysis metrics."""
    vacancy_impact: Dict[str, float]
    rate_impact: Dict[str, float]
    price_impact: Dict[str, float]
    rent_impact: Dict[str, float]

@dataclass
class ScenarioMetrics:
    """Scenario analysis metrics."""
    best_case: Dict[str, float]
    worst_case: Dict[str, float]
    expected_case: Dict[str, float]
    probability_weighted_return: float

class AdvancedMetricsCalculator:
    """Calculator for advanced investment metrics."""
    
    def __init__(
        self,
        property_price: float,
        monthly_rent: float,
        operating_expenses: Dict[str, float],
        tax_rate: float = 0.25,
        appreciation_rate: float = 0.03,
        vacancy_rate: float = 0.05
    ):
        """Initialize calculator with property details."""
        self.price = property_price
        self.monthly_rent = monthly_rent
        self.operating_expenses = operating_expenses
        self.tax_rate = tax_rate
        self.appreciation_rate = appreciation_rate
        self.vacancy_rate = vacancy_rate
    
    def calculate_tax_metrics(self, land_value_ratio: float = 0.2) -> TaxMetrics:
        """Calculate tax-related metrics."""
        # Building value (excluding land) for depreciation
        building_value = self.price * (1 - land_value_ratio)
        
        # Annual depreciation (27.5 years for residential)
        depreciation = building_value / 27.5
        
        # Calculate tax deductions
        deductions = {
            'Depreciation': depreciation,
            'Property_Tax': self.operating_expenses.get('Property_Tax', 0),
            'Insurance': self.operating_expenses.get('Insurance', 0),
            'Maintenance': self.operating_expenses.get('Maintenance', 0),
            'Property_Management': self.operating_expenses.get('Property_Management', 0)
        }
        
        # Calculate tax savings
        total_deductions = sum(deductions.values())
        tax_savings = total_deductions * self.tax_rate
        
        # Calculate effective tax rate
        gross_income = self.monthly_rent * 12
        effective_tax_rate = 1 - (tax_savings / gross_income)
        
        return TaxMetrics(
            depreciation_annual=depreciation,
            tax_savings_annual=tax_savings,
            effective_tax_rate=effective_tax_rate,
            cost_basis=self.price,
            tax_deductions=deductions
        )
    
    def calculate_sensitivity(
        self,
        vacancy_range: List[float] = None,
        rate_range: List[float] = None,
        price_range: List[float] = None,
        rent_range: List[float] = None
    ) -> SensitivityMetrics:
        """Calculate sensitivity metrics."""
        # Default ranges if not provided
        vacancy_range = vacancy_range or [0.03, 0.05, 0.07, 0.10]
        rate_range = rate_range or [0.03, 0.04, 0.05, 0.06]
        price_range = price_range or [0.9, 0.95, 1.0, 1.05, 1.1]  # Multipliers
        rent_range = rent_range or [0.9, 0.95, 1.0, 1.05, 1.1]    # Multipliers
        
        # Calculate impacts
        vacancy_impact = self._calculate_vacancy_sensitivity(vacancy_range)
        rate_impact = self._calculate_rate_sensitivity(rate_range)
        price_impact = self._calculate_price_sensitivity(price_range)
        rent_impact = self._calculate_rent_sensitivity(rent_range)
        
        return SensitivityMetrics(
            vacancy_impact=vacancy_impact,
            rate_impact=rate_impact,
            price_impact=price_impact,
            rent_impact=rent_impact
        )
    
    def calculate_scenarios(
        self,
        scenarios: Dict[str, Dict[str, float]] = None
    ) -> ScenarioMetrics:
        """Calculate scenario analysis metrics."""
        # Default scenarios if not provided
        if not scenarios:
            scenarios = {
                'best_case': {
                    'vacancy_rate': 0.03,
                    'appreciation_rate': 0.05,
                    'rent_growth': 0.04,
                    'probability': 0.25
                },
                'expected_case': {
                    'vacancy_rate': 0.05,
                    'appreciation_rate': 0.03,
                    'rent_growth': 0.02,
                    'probability': 0.50
                },
                'worst_case': {
                    'vacancy_rate': 0.08,
                    'appreciation_rate': 0.01,
                    'rent_growth': 0.01,
                    'probability': 0.25
                }
            }
        
        # Calculate returns for each scenario
        returns = {}
        weighted_return = 0
        
        for scenario, params in scenarios.items():
            # Calculate NOI
            potential_income = self.monthly_rent * 12 * (1 + params['rent_growth'])
            effective_income = potential_income * (1 - params['vacancy_rate'])
            noi = effective_income - sum(self.operating_expenses.values())
            
            # Calculate metrics for scenario
            returns[scenario] = {
                'NOI': noi,
                'Cap_Rate': noi / self.price,
                'Appreciation': self.price * params['appreciation_rate'],
                'Total_Return': (noi + (self.price * params['appreciation_rate'])) / self.price
            }
            
            # Add to weighted return
            weighted_return += returns[scenario]['Total_Return'] * params['probability']
        
        return ScenarioMetrics(
            best_case=returns['best_case'],
            worst_case=returns['worst_case'],
            expected_case=returns['expected_case'],
            probability_weighted_return=weighted_return
        )
    
    def _calculate_vacancy_sensitivity(self, vacancy_range: List[float]) -> Dict[str, float]:
        """Calculate sensitivity to vacancy rate changes."""
        results = {}
        base_noi = self.monthly_rent * 12 * (1 - self.vacancy_rate) - sum(self.operating_expenses.values())
        
        for rate in vacancy_range:
            noi = self.monthly_rent * 12 * (1 - rate) - sum(self.operating_expenses.values())
            results[f'vacancy_{rate:.2f}'] = (noi - base_noi) / base_noi
        
        return results
    
    def _calculate_rate_sensitivity(self, rate_range: List[float]) -> Dict[str, float]:
        """Calculate sensitivity to interest rate changes."""
        results = {}
        base_value = self.price * (1 + self.appreciation_rate)
        
        for rate in rate_range:
            value = self.price * (1 + rate)
            results[f'rate_{rate:.2f}'] = (value - base_value) / base_value
        
        return results
    
    def _calculate_price_sensitivity(self, price_range: List[float]) -> Dict[str, float]:
        """Calculate sensitivity to price changes."""
        results = {}
        base_metrics = {
            'cap_rate': (self.monthly_rent * 12) / self.price,
            'price_to_rent': self.price / (self.monthly_rent * 12)
        }
        
        for multiplier in price_range:
            new_price = self.price * multiplier
            results[f'price_{multiplier:.2f}'] = {
                'cap_rate': (self.monthly_rent * 12) / new_price,
                'price_to_rent': new_price / (self.monthly_rent * 12),
                'change': (new_price - self.price) / self.price
            }
        
        return results
    
    def _calculate_rent_sensitivity(self, rent_range: List[float]) -> Dict[str, float]:
        """Calculate sensitivity to rent changes."""
        results = {}
        base_noi = self.monthly_rent * 12 * (1 - self.vacancy_rate) - sum(self.operating_expenses.values())
        
        for multiplier in rent_range:
            new_rent = self.monthly_rent * multiplier
            noi = new_rent * 12 * (1 - self.vacancy_rate) - sum(self.operating_expenses.values())
            results[f'rent_{multiplier:.2f}'] = (noi - base_noi) / base_noi
        
        return results
