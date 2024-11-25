"""Analysis utilities for real estate investment calculations."""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from src.models.investment import Investment, InvestmentAssumptions
from src.models.property import PropertyDetails

@dataclass
class AnalysisResults:
    """Container for analysis results."""
    metrics: Dict[str, float]
    cash_flows: pd.DataFrame
    amortization: pd.DataFrame
    operating_expenses: Dict[str, float]
    monthly_rent: float
    monthly_mortgage: float
    total_investment: float
    projected_value: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis results to dictionary."""
        return {
            'metrics': self.metrics,
            'cash_flows': self.cash_flows.to_dict('records'),
            'amortization': self.amortization.to_dict('records'),
            'operating_expenses': self.operating_expenses,
            'monthly_rent': self.monthly_rent,
            'monthly_mortgage': self.monthly_mortgage,
            'total_investment': self.total_investment,
            'projected_value': self.projected_value
        }

class PropertyAnalyzer:
    """Property analysis utility class."""
    
    def __init__(self, property_details: PropertyDetails, assumptions: InvestmentAssumptions):
        """Initialize analyzer with property details and assumptions."""
        self.property = property_details
        self.assumptions = assumptions
        self.investment = Investment(self.property.zpid, self.assumptions)
    
    def analyze(self, project_life: int = 5) -> AnalysisResults:
        """Perform comprehensive property analysis."""
        # Calculate loan details
        loan_amount = self.property.price * (1 - self.assumptions.equity_percentage / 100)
        monthly_mortgage = self.assumptions.calculate_monthly_payment(loan_amount)
        
        # Calculate monthly rent (use Zillow estimate if available)
        monthly_rent = self.property.rent_estimate or self.estimate_rent()
        
        # Calculate metrics
        metrics = self.investment.calculate_metrics(
            self.property.price,
            monthly_rent,
            project_life
        )
        
        # Calculate cash flows and amortization
        cash_flows = self.investment.calculate_cash_flows(
            self.property.price,
            monthly_rent,
            project_life
        )
        amortization = self.investment.calculate_amortization(loan_amount)
        
        # Calculate operating expenses
        operating_expenses = self.calculate_operating_expenses(monthly_rent)
        
        # Calculate total investment required
        total_investment = (
            self.property.price * (self.assumptions.equity_percentage / 100) +
            self.assumptions.renovation_budget +
            self.assumptions.cash_reserves +
            self.assumptions.extra_cash_reserves
        )
        
        # Calculate projected value
        projected_value = self.calculate_projected_value(project_life)
        
        return AnalysisResults(
            metrics=metrics,
            cash_flows=cash_flows,
            amortization=amortization,
            operating_expenses=operating_expenses,
            monthly_rent=monthly_rent,
            monthly_mortgage=monthly_mortgage,
            total_investment=total_investment,
            projected_value=projected_value
        )
    
    def estimate_rent(self) -> float:
        """Estimate monthly rent based on property details."""
        # Simple rent estimation (1% rule as fallback)
        return self.property.price * 0.01
    
    def calculate_operating_expenses(self, monthly_rent: float) -> Dict[str, float]:
        """Calculate annual operating expenses."""
        effective_rent = monthly_rent * 12 * (1 - self.assumptions.vacancy_rate)
        
        return {
            'Property_Management': effective_rent * self.assumptions.property_mgmt_rate,
            'Maintenance': effective_rent * self.assumptions.maintenance_rate,
            'Vacancy_Loss': monthly_rent * 12 * self.assumptions.vacancy_rate,
            'Property_Tax': self.property.price * 0.015,  # Estimated annual property tax
            'Insurance': self.property.price * 0.005,  # Estimated annual insurance
            'Total_Expenses': sum([
                effective_rent * self.assumptions.property_mgmt_rate,
                effective_rent * self.assumptions.maintenance_rate,
                monthly_rent * 12 * self.assumptions.vacancy_rate,
                self.property.price * 0.015,
                self.property.price * 0.005
            ])
        }
    
    def calculate_projected_value(self, years: int) -> float:
        """Calculate projected property value after specified years."""
        return self.property.price * (1 + self.assumptions.rental_growth_rate) ** years

class InvestmentVisualizer:
    """Visualization utility class for investment analysis."""
    
    @staticmethod
    def plot_cash_flows(cash_flows: pd.DataFrame) -> go.Figure:
        """Create cash flow visualization."""
        fig = go.Figure()
        
        # Add bar chart for cash flows
        fig.add_trace(go.Bar(
            x=cash_flows['Year'],
            y=cash_flows['Cash Flow'],
            name='Cash Flow',
            marker_color=['red' if cf < 0 else 'green' for cf in cash_flows['Cash Flow']]
        ))
        
        # Add cumulative line
        cumulative = cash_flows['Cash Flow'].cumsum()
        fig.add_trace(go.Scatter(
            x=cash_flows['Year'],
            y=cumulative,
            name='Cumulative Cash Flow',
            line=dict(color='blue')
        ))
        
        fig.update_layout(
            title='Cash Flow Analysis',
            xaxis_title='Year',
            yaxis_title='Amount ($)',
            barmode='group',
            hovermode='x'
        )
        
        return fig
    
    @staticmethod
    def plot_amortization(amortization: pd.DataFrame) -> go.Figure:
        """Create loan amortization visualization."""
        fig = go.Figure()
        
        # Add principal and interest traces
        fig.add_trace(go.Bar(
            x=amortization['Period'],
            y=amortization['Principal'],
            name='Principal',
            marker_color='blue'
        ))
        
        fig.add_trace(go.Bar(
            x=amortization['Period'],
            y=amortization['Interest'],
            name='Interest',
            marker_color='red'
        ))
        
        # Add balance line
        fig.add_trace(go.Scatter(
            x=amortization['Period'],
            y=amortization['Balance'],
            name='Loan Balance',
            line=dict(color='green')
        ))
        
        fig.update_layout(
            title='Loan Amortization Schedule',
            xaxis_title='Period (Months)',
            yaxis_title='Amount ($)',
            barmode='stack',
            hovermode='x'
        )
        
        return fig
    
    @staticmethod
    def plot_operating_expenses(expenses: Dict[str, float]) -> go.Figure:
        """Create operating expenses visualization."""
        # Remove total from pie chart
        expenses_for_plot = {k: v for k, v in expenses.items() if k != 'Total_Expenses'}
        
        fig = go.Figure(data=[go.Pie(
            labels=list(expenses_for_plot.keys()),
            values=list(expenses_for_plot.values()),
            hole=.3
        )])
        
        fig.update_layout(
            title='Operating Expenses Breakdown',
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def plot_metrics_radar(metrics: Dict[str, float]) -> go.Figure:
        """Create metrics radar chart."""
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=[
                metrics.get('IRR', 0) * 100,  # Convert to percentage
                metrics.get('Cash_on_Cash', 0),
                metrics.get('NPV', 0) / 1000,  # Scale down for visualization
                metrics.get('ROI', 0)
            ],
            theta=['IRR', 'Cash on Cash', 'NPV (000s)', 'ROI'],
            fill='toself'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max([
                        metrics.get('IRR', 0) * 100,
                        metrics.get('Cash_on_Cash', 0),
                        metrics.get('NPV', 0) / 1000,
                        metrics.get('ROI', 0)
                    ])]
                )
            ),
            showlegend=False,
            title='Investment Metrics Overview'
        )
        
        return fig
