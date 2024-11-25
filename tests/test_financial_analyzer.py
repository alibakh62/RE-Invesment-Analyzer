"""Tests for financial analyzer module."""
import unittest
from datetime import datetime
from pathlib import Path

from src.models.property import PropertyDetails
from src.models.investment import InvestmentAssumptions
from src.analysis.financial_analyzer import FinancialAnalyzer
from src.analysis.advanced_metrics import AdvancedMetricsCalculator

class TestFinancialAnalyzer(unittest.TestCase):
    """Test cases for FinancialAnalyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.property_details = PropertyDetails(
            zpid="test123",
            address="123 Test St",
            price=500000,
            bedrooms=3,
            bathrooms=2,
            square_feet=2000,
            year_built=2000,
            property_type="Single Family",
            rent_estimate=2500
        )
        
        self.assumptions = InvestmentAssumptions(
            equity_percentage=20,
            cash_reserves=10000,
            amortization_period=30,
            interest_rate=0.045,
            rental_growth_rate=0.02,
            expense_growth_rate=0.02,
            vacancy_rate=0.05,
            property_mgmt_rate=0.10,
            maintenance_rate=0.05
        )
        
        self.analyzer = FinancialAnalyzer(
            property_details=self.property_details,
            investment_assumptions=self.assumptions
        )
    
    def test_analyze_returns_valid_results(self):
        """Test that analyze() returns valid results."""
        results = self.analyzer.analyze()
        
        # Test that all required attributes exist
        self.assertIsNotNone(results.financial_metrics)
        self.assertIsNotNone(results.analysis_results)
        
        # Test that metrics are within reasonable ranges
        metrics = results.financial_metrics
        self.assertGreater(metrics.cap_rate, 0)
        self.assertLess(metrics.cap_rate, 100)
        self.assertGreater(metrics.cash_on_cash_return, -100)
        self.assertLess(metrics.cash_on_cash_return, 100)
        self.assertGreater(metrics.debt_coverage_ratio, 0)
    
    def test_cash_flow_calculation(self):
        """Test cash flow calculations."""
        results = self.analyzer.analyze()
        cash_flows = results.analysis_results.cash_flows
        
        # Test that we have the expected number of cash flows
        self.assertEqual(len(cash_flows), 6)  # Initial + 5 years
        
        # Test that initial cash flow is negative (down payment)
        self.assertLess(cash_flows.iloc[0]['Cash Flow'], 0)
        
        # Test that operating cash flows are reasonable
        for i in range(1, len(cash_flows)):
            cf = cash_flows.iloc[i]['Cash Flow']
            annual_rent = self.property_details.rent_estimate * 12
            self.assertLess(cf, annual_rent)  # Cash flow should be less than gross rent
            self.assertGreater(cf, -annual_rent)  # Cash flow shouldn't be more negative than gross rent
    
    def test_risk_metrics(self):
        """Test risk metric calculations."""
        results = self.analyzer.analyze()
        metrics = results.financial_metrics
        
        # Test default risk score
        self.assertGreaterEqual(metrics.default_risk_score, 0)
        self.assertLessEqual(metrics.default_risk_score, 100)
        
        # Test debt coverage ratio
        self.assertGreater(metrics.debt_coverage_ratio, 0)
        
        # Test break even ratio
        self.assertGreater(metrics.break_even_ratio, 0)
        self.assertLess(metrics.break_even_ratio, 2)  # Shouldn't take more than 2x gross rent to break even
    
    def test_market_analysis(self):
        """Test market analysis with comparable properties."""
        comparable_properties = [
            PropertyDetails(
                zpid=str(i),
                address=f"{i} Comp St",
                price=500000 + (i * 10000),
                bedrooms=3,
                bathrooms=2,
                square_feet=2000,
                year_built=2000,
                property_type="Single Family",
                rent_estimate=2500
            ) for i in range(1, 4)
        ]
        
        analyzer = FinancialAnalyzer(
            property_details=self.property_details,
            investment_assumptions=self.assumptions,
            comparable_properties=comparable_properties
        )
        
        results = analyzer.analyze()
        
        # Test that market metrics exist
        self.assertIsNotNone(results.market_metrics)
        self.assertIsNotNone(results.financial_metrics.market_position)
        
        # Test market position calculations
        position = results.financial_metrics.market_position
        self.assertIn('price_vs_median', position)
        self.assertIn('ppsf_vs_median', position)

class TestAdvancedMetrics(unittest.TestCase):
    """Test cases for AdvancedMetricsCalculator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = AdvancedMetricsCalculator(
            property_price=500000,
            monthly_rent=2500,
            operating_expenses={
                'Property_Tax': 6000,
                'Insurance': 2000,
                'Maintenance': 3000,
                'Property_Management': 3000
            }
        )
    
    def test_tax_metrics(self):
        """Test tax metric calculations."""
        metrics = self.calculator.calculate_tax_metrics()
        
        # Test depreciation calculation
        expected_depreciation = (500000 * 0.8) / 27.5  # 80% of price / 27.5 years
        self.assertAlmostEqual(metrics.depreciation_annual, expected_depreciation, places=2)
        
        # Test tax savings
        self.assertGreater(metrics.tax_savings_annual, 0)
        self.assertLess(metrics.effective_tax_rate, 1)
    
    def test_sensitivity_analysis(self):
        """Test sensitivity analysis calculations."""
        metrics = self.calculator.calculate_sensitivity()
        
        # Test that all sensitivity metrics exist
        self.assertIsNotNone(metrics.vacancy_impact)
        self.assertIsNotNone(metrics.rate_impact)
        self.assertIsNotNone(metrics.price_impact)
        self.assertIsNotNone(metrics.rent_impact)
        
        # Test that impacts are reasonable
        for impact in metrics.vacancy_impact.values():
            self.assertLessEqual(abs(impact), 1)  # Impact shouldn't be more than 100%
    
    def test_scenario_analysis(self):
        """Test scenario analysis calculations."""
        metrics = self.calculator.calculate_scenarios()
        
        # Test that all scenarios exist
        self.assertIsNotNone(metrics.best_case)
        self.assertIsNotNone(metrics.worst_case)
        self.assertIsNotNone(metrics.expected_case)
        
        # Test scenario relationships
        self.assertGreater(
            metrics.best_case['Total_Return'],
            metrics.expected_case['Total_Return']
        )
        self.assertGreater(
            metrics.expected_case['Total_Return'],
            metrics.worst_case['Total_Return']
        )
        
        # Test probability weighted return
        self.assertGreater(metrics.probability_weighted_return, 0)
        self.assertLess(metrics.probability_weighted_return, 1)  # Should be less than 100% return

if __name__ == '__main__':
    unittest.main()
