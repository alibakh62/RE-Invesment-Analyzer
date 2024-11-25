"""Report generator for real estate investment analysis."""
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime
import plotly.io as pio

from src.analysis.financial_analyzer import FinancialAnalysis
from src.utils.market_analysis import MarketVisualizer
from src.utils.logging_config import logger_config

# Get logger
logger = logger_config.get_logger('report_generator')

class ReportGenerator:
    """Generate detailed investment analysis reports."""
    
    def __init__(self, analysis: FinancialAnalysis):
        """Initialize report generator."""
        self.analysis = analysis
        self.visualizer = MarketVisualizer()
    
    def generate_html_report(self, output_path: Path) -> None:
        """Generate HTML report with interactive visualizations."""
        logger.info(f"Generating HTML report for property {self.analysis.property_details.zpid}")
        
        try:
            # Create report sections
            sections = []
            
            # Property Overview
            sections.append(self._create_property_overview())
            
            # Financial Summary
            sections.append(self._create_financial_summary())
            
            # Investment Analysis
            sections.append(self._create_investment_analysis())
            
            # Market Analysis
            if self.analysis.market_metrics:
                sections.append(self._create_market_analysis())
            
            # Risk Analysis
            sections.append(self._create_risk_analysis())
            
            # Combine sections and save
            html_content = self._combine_sections(sections)
            output_path.write_text(html_content)
            logger.info(f"Report generated successfully at {output_path}")
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}", exc_info=True)
            raise
    
    def _create_property_overview(self) -> str:
        """Create property overview section."""
        prop = self.analysis.property_details
        
        return f"""
        <div class="section">
            <h2>Property Overview</h2>
            <div class="property-details">
                <div class="address">{prop.address}</div>
                <div class="price">${prop.price:,.2f}</div>
                <div class="specs">
                    <span>{prop.bedrooms} beds</span>
                    <span>{prop.bathrooms} baths</span>
                    <span>{prop.square_feet:,.0f} sqft</span>
                    <span>Built {prop.year_built}</span>
                </div>
                <div class="estimates">
                    <div>Zestimate: ${prop.zestimate:,.2f}</div>
                    <div>Rent Estimate: ${prop.rent_estimate:,.2f}/month</div>
                </div>
            </div>
        </div>
        """
    
    def _create_financial_summary(self) -> str:
        """Create financial summary section."""
        metrics = self.analysis.financial_metrics
        
        return f"""
        <div class="section">
            <h2>Financial Summary</h2>
            <div class="metrics-grid">
                <div class="metric">
                    <div class="label">Cap Rate</div>
                    <div class="value">{metrics.cap_rate:.1f}%</div>
                </div>
                <div class="metric">
                    <div class="label">Cash on Cash Return</div>
                    <div class="value">{metrics.cash_on_cash_return:.1f}%</div>
                </div>
                <div class="metric">
                    <div class="label">IRR (5yr)</div>
                    <div class="value">{metrics.irr:.1f}%</div>
                </div>
                <div class="metric">
                    <div class="label">Total ROI (5yr)</div>
                    <div class="value">{metrics.total_roi:.1f}%</div>
                </div>
            </div>
            {self._plot_cash_flows()}
        </div>
        """
    
    def _create_investment_analysis(self) -> str:
        """Create investment analysis section."""
        results = self.analysis.analysis_results
        
        return f"""
        <div class="section">
            <h2>Investment Analysis</h2>
            <div class="investment-details">
                <div class="subsection">
                    <h3>Monthly Cash Flow</h3>
                    <div class="cash-flow-details">
                        <div>Rental Income: ${results.monthly_rent:,.2f}</div>
                        <div>Mortgage Payment: ${results.monthly_mortgage:,.2f}</div>
                        <div>Operating Expenses: ${results.operating_expenses['Total_Expenses']/12:,.2f}</div>
                        <div class="net-cash-flow">Net Cash Flow: ${results.monthly_rent - results.monthly_mortgage - results.operating_expenses['Total_Expenses']/12:,.2f}</div>
                    </div>
                </div>
                {self._plot_operating_expenses()}
                {self._plot_amortization()}
            </div>
        </div>
        """
    
    def _create_market_analysis(self) -> str:
        """Create market analysis section."""
        metrics = self.analysis.market_metrics
        position = self.analysis.financial_metrics.market_position
        
        return f"""
        <div class="section">
            <h2>Market Analysis</h2>
            <div class="market-metrics">
                <div class="metric">
                    <div class="label">Price vs. Market</div>
                    <div class="value">{position.get('price_vs_median', 0):.1f}%</div>
                </div>
                <div class="metric">
                    <div class="label">Price/SqFt vs. Market</div>
                    <div class="value">{position.get('ppsf_vs_median', 0):.1f}%</div>
                </div>
                <div class="metric">
                    <div class="label">Days on Market</div>
                    <div class="value">{metrics.days_on_market['median']:.0f}</div>
                </div>
            </div>
            {self._plot_market_comparison()}
        </div>
        """
    
    def _create_risk_analysis(self) -> str:
        """Create risk analysis section."""
        metrics = self.analysis.financial_metrics
        
        return f"""
        <div class="section">
            <h2>Risk Analysis</h2>
            <div class="risk-metrics">
                <div class="metric">
                    <div class="label">Default Risk Score</div>
                    <div class="value">{metrics.default_risk_score:.0f}/100</div>
                </div>
                <div class="metric">
                    <div class="label">Debt Coverage Ratio</div>
                    <div class="value">{metrics.debt_coverage_ratio:.2f}</div>
                </div>
                <div class="metric">
                    <div class="label">Break Even Ratio</div>
                    <div class="value">{metrics.break_even_ratio:.2f}</div>
                </div>
                <div class="metric">
                    <div class="label">Price to Rent Ratio</div>
                    <div class="value">{metrics.price_to_rent_ratio:.1f}</div>
                </div>
            </div>
            {self._plot_risk_metrics()}
        </div>
        """
    
    def _plot_cash_flows(self) -> str:
        """Create cash flow visualization."""
        fig = self.visualizer.plot_cash_flows(self.analysis.analysis_results.cash_flows)
        return self._figure_to_html(fig)
    
    def _plot_operating_expenses(self) -> str:
        """Create operating expenses visualization."""
        fig = self.visualizer.plot_operating_expenses(
            self.analysis.analysis_results.operating_expenses
        )
        return self._figure_to_html(fig)
    
    def _plot_amortization(self) -> str:
        """Create amortization visualization."""
        fig = self.visualizer.plot_amortization(
            self.analysis.analysis_results.amortization
        )
        return self._figure_to_html(fig)
    
    def _plot_market_comparison(self) -> str:
        """Create market comparison visualization."""
        if not self.analysis.comparable_properties:
            return ""
        
        fig = self.visualizer.plot_property_comparison(
            self.analysis.property_details,
            self.analysis.comparable_properties
        )
        return self._figure_to_html(fig)
    
    def _plot_risk_metrics(self) -> str:
        """Create risk metrics visualization."""
        fig = self.visualizer.plot_metrics_radar(
            self.analysis.financial_metrics.to_dict()['risk_metrics']
        )
        return self._figure_to_html(fig)
    
    def _figure_to_html(self, fig: go.Figure) -> str:
        """Convert plotly figure to HTML."""
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    def _combine_sections(self, sections: List[str]) -> str:
        """Combine report sections with styling."""
        css = """
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }
            .section {
                background: white;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h2 {
                color: #333;
                margin-top: 0;
                border-bottom: 2px solid #eee;
                padding-bottom: 10px;
            }
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            .metric {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 6px;
                text-align: center;
            }
            .metric .label {
                color: #666;
                font-size: 0.9em;
                margin-bottom: 5px;
            }
            .metric .value {
                font-size: 1.4em;
                font-weight: bold;
                color: #333;
            }
            .property-details {
                text-align: center;
                margin-bottom: 20px;
            }
            .address {
                font-size: 1.2em;
                margin-bottom: 10px;
            }
            .price {
                font-size: 1.8em;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
            .specs {
                display: flex;
                justify-content: center;
                gap: 20px;
                margin-bottom: 10px;
            }
            .specs span {
                background: #e9ecef;
                padding: 5px 10px;
                border-radius: 4px;
            }
            .cash-flow-details {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 6px;
                margin: 10px 0;
            }
            .net-cash-flow {
                font-weight: bold;
                margin-top: 10px;
                padding-top: 10px;
                border-top: 1px solid #ddd;
            }
        </style>
        """
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"""
        <div class="section">
            <h1>Real Estate Investment Analysis Report</h1>
            <p>Generated on {timestamp}</p>
        </div>
        """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Investment Analysis Report</title>
            {css}
        </head>
        <body>
            {header}
            {''.join(sections)}
        </body>
        </html>
        """
