"""Financial analysis module for real estate investment."""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import pandas as pd
import numpy as np
from datetime import datetime

from src.models.property import PropertyDetails
from src.models.investment import Investment, InvestmentAssumptions
from src.utils.analysis import PropertyAnalyzer, AnalysisResults
from src.utils.market_analysis import MarketAnalyzer, MarketMetrics, MarketVisualizer
from src.utils.logging_config import logger_config

# Get logger
logger = logger_config.get_logger('financial_analysis')

@dataclass
class FinancialMetrics:
    """Container for comprehensive financial metrics."""
    # Return metrics
    cap_rate: float
    cash_on_cash_return: float
    total_roi: float
    irr: float
    npv: float
    payback_period: float
    
    # Risk metrics
    debt_coverage_ratio: float
    break_even_ratio: float
    default_risk_score: float
    price_to_rent_ratio: float
    
    # Growth metrics
    equity_growth_5yr: float
    appreciation_5yr: float
    rent_growth_5yr: float
    total_return_5yr: float
    
    # Market metrics
    market_position: Dict[str, float]
    price_per_sqft_ratio: float
    rent_per_sqft_ratio: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'return_metrics': {
                'cap_rate': self.cap_rate,
                'cash_on_cash_return': self.cash_on_cash_return,
                'total_roi': self.total_roi,
                'irr': self.irr,
                'npv': self.npv,
                'payback_period': self.payback_period
            },
            'risk_metrics': {
                'debt_coverage_ratio': self.debt_coverage_ratio,
                'break_even_ratio': self.break_even_ratio,
                'default_risk_score': self.default_risk_score,
                'price_to_rent_ratio': self.price_to_rent_ratio
            },
            'growth_metrics': {
                'equity_growth_5yr': self.equity_growth_5yr,
                'appreciation_5yr': self.appreciation_5yr,
                'rent_growth_5yr': self.rent_growth_5yr,
                'total_return_5yr': self.total_return_5yr
            },
            'market_metrics': {
                'market_position': self.market_position,
                'price_per_sqft_ratio': self.price_per_sqft_ratio,
                'rent_per_sqft_ratio': self.rent_per_sqft_ratio
            }
        }

@dataclass
class FinancialAnalysis:
    """Container for comprehensive financial analysis."""
    property_details: PropertyDetails
    investment_assumptions: InvestmentAssumptions
    financial_metrics: FinancialMetrics
    analysis_results: AnalysisResults
    market_metrics: Optional[MarketMetrics] = None
    comparable_properties: Optional[List[PropertyDetails]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis to dictionary."""
        return {
            'property_details': self.property_details.__dict__,
            'investment_assumptions': self.investment_assumptions.to_dict(),
            'financial_metrics': self.financial_metrics.to_dict(),
            'analysis_results': self.analysis_results.to_dict(),
            'market_metrics': self.market_metrics.__dict__ if self.market_metrics else None,
            'comparable_properties': [p.__dict__ for p in self.comparable_properties] if self.comparable_properties else None
        }

class FinancialAnalyzer:
    """Comprehensive financial analysis utility."""
    
    def __init__(
        self,
        property_details: PropertyDetails,
        investment_assumptions: InvestmentAssumptions,
        comparable_properties: Optional[List[PropertyDetails]] = None
    ):
        """Initialize financial analyzer."""
        self.property = property_details
        self.assumptions = investment_assumptions
        self.comparable_properties = comparable_properties
        
        # Initialize analyzers
        self.property_analyzer = PropertyAnalyzer(property_details, investment_assumptions)
        if comparable_properties:
            self.market_analyzer = MarketAnalyzer(comparable_properties)
        else:
            self.market_analyzer = None
    
    def analyze(self, project_life: int = 5) -> FinancialAnalysis:
        """Perform comprehensive financial analysis."""
        logger.info(f"Starting financial analysis for property {self.property.zpid}")
        
        try:
            # Get property analysis results
            analysis_results = self.property_analyzer.analyze(project_life)
            
            # Calculate financial metrics
            financial_metrics = self._calculate_financial_metrics(analysis_results)
            
            # Get market metrics if available
            market_metrics = None
            if self.market_analyzer:
                market_metrics = self.market_analyzer.calculate_market_metrics()
                market_position = self.market_analyzer.analyze_property_position(self.property)
                financial_metrics.market_position = market_position
            
            return FinancialAnalysis(
                property_details=self.property,
                investment_assumptions=self.assumptions,
                financial_metrics=financial_metrics,
                analysis_results=analysis_results,
                market_metrics=market_metrics,
                comparable_properties=self.comparable_properties
            )
            
        except Exception as e:
            logger.error(f"Error during financial analysis: {str(e)}", exc_info=True)
            raise
    
    def _calculate_financial_metrics(self, results: AnalysisResults) -> FinancialMetrics:
        """Calculate comprehensive financial metrics."""
        # Get base metrics from results
        metrics = results.metrics
        
        # Calculate additional metrics
        annual_noi = (results.monthly_rent * 12) - results.operating_expenses['Total_Expenses']
        annual_debt_service = results.monthly_mortgage * 12
        
        return FinancialMetrics(
            # Return metrics
            cap_rate=annual_noi / self.property.price * 100,
            cash_on_cash_return=metrics['Cash_on_Cash'],
            total_roi=metrics.get('ROI', 0),
            irr=metrics['IRR'] * 100,
            npv=metrics['NPV'],
            payback_period=self._calculate_payback_period(results.cash_flows),
            
            # Risk metrics
            debt_coverage_ratio=annual_noi / annual_debt_service,
            break_even_ratio=self._calculate_break_even_ratio(results),
            default_risk_score=self._calculate_default_risk(results),
            price_to_rent_ratio=self.property.price / (results.monthly_rent * 12),
            
            # Growth metrics
            equity_growth_5yr=self._calculate_equity_growth(results),
            appreciation_5yr=results.projected_value / self.property.price - 1,
            rent_growth_5yr=(1 + self.assumptions.rental_growth_rate) ** 5 - 1,
            total_return_5yr=self._calculate_total_return(results),
            
            # Market metrics (placeholder values, updated later if market data available)
            market_position={},
            price_per_sqft_ratio=0.0,
            rent_per_sqft_ratio=0.0
        )
    
    def _calculate_payback_period(self, cash_flows: pd.DataFrame) -> float:
        """Calculate payback period in years."""
        cumulative = cash_flows['Cash Flow'].cumsum()
        if all(cumulative < 0):
            return float('inf')
        
        # Find the first positive cumulative cash flow
        positive_year = cumulative[cumulative > 0].index[0]
        if positive_year == 0:
            return 0.0
        
        # Interpolate for more accurate payback period
        prev_cf = cumulative.iloc[positive_year - 1]
        curr_cf = cumulative.iloc[positive_year]
        fraction = abs(prev_cf) / (curr_cf - prev_cf)
        
        return positive_year - 1 + fraction
    
    def _calculate_break_even_ratio(self, results: AnalysisResults) -> float:
        """Calculate break-even ratio."""
        annual_debt_service = results.monthly_mortgage * 12
        annual_operating_expenses = results.operating_expenses['Total_Expenses']
        potential_gross_income = results.monthly_rent * 12
        
        return (annual_debt_service + annual_operating_expenses) / potential_gross_income
    
    def _calculate_default_risk(self, results: AnalysisResults) -> float:
        """Calculate default risk score (0-100, lower is better)."""
        # Factors to consider
        dcr = annual_noi = (results.monthly_rent * 12 - results.operating_expenses['Total_Expenses']) / (results.monthly_mortgage * 12)
        ltv = (1 - self.assumptions.equity_percentage / 100)
        debt_burden = results.monthly_mortgage / results.monthly_rent
        
        # Weight the factors
        risk_score = (
            (max(0, 1.25 - dcr) * 40) +  # DCR below 1.25 increases risk
            (ltv * 30) +                  # Higher LTV increases risk
            (debt_burden * 30)            # Higher debt burden increases risk
        )
        
        return min(100, max(0, risk_score))
    
    def _calculate_equity_growth(self, results: AnalysisResults) -> float:
        """Calculate 5-year equity growth rate."""
        initial_equity = self.property.price * (self.assumptions.equity_percentage / 100)
        loan_amount = self.property.price - initial_equity
        
        # Get loan balance after 5 years
        amort_5yr = results.amortization[results.amortization['Period'] == 60]
        remaining_balance = amort_5yr['Balance'].iloc[0] if not amort_5yr.empty else loan_amount
        
        # Calculate equity after 5 years
        future_equity = results.projected_value - remaining_balance
        
        return (future_equity / initial_equity) - 1
    
    def _calculate_total_return(self, results: AnalysisResults) -> float:
        """Calculate 5-year total return including cash flows and appreciation."""
        # Sum of all cash flows
        total_cash_flows = results.cash_flows['Cash Flow'].sum()
        
        # Add appreciation
        appreciation = results.projected_value - self.property.price
        
        # Calculate return relative to initial investment
        initial_investment = self.property.price * (self.assumptions.equity_percentage / 100)
        
        return (total_cash_flows + appreciation) / initial_investment
