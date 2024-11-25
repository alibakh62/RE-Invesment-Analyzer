"""Visualization utilities for investment analysis."""
from typing import Dict, List, Optional, Any
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

class InvestmentVisualizer:
    """Create interactive visualizations for investment analysis."""
    
    @staticmethod
    def plot_cash_flows(cash_flows: pd.DataFrame) -> go.Figure:
        """Create cash flow visualization."""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Annual Cash Flows', 'Cumulative Cash Flow'),
            vertical_spacing=0.12
        )
        
        # Annual cash flows
        fig.add_trace(
            go.Bar(
                name='Cash Flow',
                x=cash_flows['Year'],
                y=cash_flows['Cash_Flow'],
                marker_color='rgb(55, 83, 109)'
            ),
            row=1, col=1
        )
        
        # Cumulative cash flow
        cumulative = cash_flows['Cash_Flow'].cumsum()
        fig.add_trace(
            go.Scatter(
                name='Cumulative',
                x=cash_flows['Year'],
                y=cumulative,
                mode='lines+markers',
                line=dict(color='rgb(26, 118, 255)')
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title='Investment Cash Flows',
            showlegend=True,
            height=800
        )
        
        return fig
    
    @staticmethod
    def plot_metrics_radar(metrics: Dict[str, float]) -> go.Figure:
        """Create radar chart of investment metrics."""
        categories = ['IRR', 'Cap Rate', 'Cash on Cash', 'ROI', 'Debt Coverage']
        values = [
            metrics['IRR'],
            metrics['Cap_Rate'],
            metrics['Cash_on_Cash'],
            metrics['ROI'],
            metrics['Debt_Service_Coverage'] * 100
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Investment Metrics'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(values) * 1.2]
                )
            ),
            showlegend=False,
            title='Investment Metrics Overview'
        )
        
        return fig
    
    @staticmethod
    def plot_amortization(amortization: pd.DataFrame) -> go.Figure:
        """Create amortization schedule visualization."""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Monthly Payments Breakdown', 'Loan Balance'),
            vertical_spacing=0.12
        )
        
        # Monthly payment breakdown
        fig.add_trace(
            go.Bar(
                name='Principal',
                x=amortization['Period'],
                y=amortization['Principal'],
                marker_color='rgb(55, 83, 109)'
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(
                name='Interest',
                x=amortization['Period'],
                y=amortization['Interest'],
                marker_color='rgb(26, 118, 255)'
            ),
            row=1, col=1
        )
        
        # Loan balance
        fig.add_trace(
            go.Scatter(
                name='Balance',
                x=amortization['Period'],
                y=amortization['Balance'],
                mode='lines',
                line=dict(color='rgb(26, 118, 255)')
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            barmode='stack',
            title='Loan Amortization Schedule',
            showlegend=True,
            height=800
        )
        
        return fig
    
    @staticmethod
    def plot_operating_expenses(expenses: Dict[str, float]) -> go.Figure:
        """Create operating expenses breakdown visualization."""
        # Remove total from pie chart
        expenses_for_plot = {k: v for k, v in expenses.items() 
                           if k != 'Total_Expenses' and v > 0}
        
        fig = go.Figure(data=[go.Pie(
            labels=list(expenses_for_plot.keys()),
            values=list(expenses_for_plot.values()),
            hole=.3
        )])
        
        fig.update_layout(
            title='Operating Expenses Breakdown',
            annotations=[dict(text=f'Total: ${expenses["Total_Expenses"]:,.2f}', 
                            x=0.5, y=0.5, font_size=14, showarrow=False)]
        )
        
        return fig
    
    @staticmethod
    def plot_property_comparison(
        properties: pd.DataFrame,
        metric: str = 'IRR',
        top_n: int = 10
    ) -> go.Figure:
        """Create property comparison visualization."""
        # Sort and get top N properties
        df = properties.nlargest(top_n, metric)
        
        fig = go.Figure(data=[
            go.Bar(
                x=df['Address'],
                y=df[metric],
                text=df[metric].round(2),
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title=f'Top {top_n} Properties by {metric}',
            xaxis_title='Property',
            yaxis_title=metric,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def plot_investment_summary(analysis: Dict[str, Any]) -> Dict[str, go.Figure]:
        """Create comprehensive investment summary visualizations."""
        return {
            'cash_flows': InvestmentVisualizer.plot_cash_flows(analysis['cash_flows']),
            'metrics': InvestmentVisualizer.plot_metrics_radar(analysis['metrics'].__dict__),
            'amortization': InvestmentVisualizer.plot_amortization(analysis['amortization']),
            'expenses': InvestmentVisualizer.plot_operating_expenses(analysis['operating_expenses'])
        }
    
    @staticmethod
    def plot_sensitivity_analysis(
        base_metrics: Dict[str, float],
        variables: List[str],
        ranges: Dict[str, List[float]]
    ) -> go.Figure:
        """Create sensitivity analysis visualization."""
        fig = go.Figure()
        
        for var in variables:
            values = ranges[var]
            metrics = []
            
            # Calculate metrics for each value
            for val in values:
                # Placeholder for actual calculation
                metric_change = (val - base_metrics[var]) / base_metrics[var] * 100
                metrics.append(metric_change)
            
            fig.add_trace(go.Scatter(
                name=var,
                x=values,
                y=metrics,
                mode='lines+markers'
            ))
        
        fig.update_layout(
            title='Sensitivity Analysis',
            xaxis_title='Variable Value',
            yaxis_title='Metric Change (%)',
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def create_metric_card(
        label: str,
        value: float,
        prefix: str = '',
        suffix: str = '',
        decimals: int = 2
    ) -> Dict[str, Any]:
        """Create a metric card for Streamlit."""
        return {
            'label': label,
            'value': f"{prefix}{value:.{decimals}f}{suffix}",
            'delta': None  # Could add comparison to market/previous
        }
