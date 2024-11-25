"""Example usage of the Real Estate Investment Analyzer."""
from pathlib import Path
from datetime import datetime

from src.models.property import PropertyDetails
from src.models.investment import InvestmentAssumptions
from src.analysis.financial_analyzer import FinancialAnalyzer
from src.analysis.advanced_metrics import AdvancedMetricsCalculator
from src.analysis.report_generator import ReportGenerator

def main():
    """Run example analysis."""
    # Create example property
    property_details = PropertyDetails(
        zpid="123456789",
        address="123 Main St, Anytown, USA",
        price=500000,
        bedrooms=3,
        bathrooms=2,
        square_feet=2000,
        lot_size=5000,
        year_built=2000,
        property_type="Single Family",
        zestimate=510000,
        rent_estimate=2500,
        last_sold_price=450000,
        last_sold_date=datetime(2020, 1, 1),
        days_on_zillow=30,
        latitude=37.7749,
        longitude=-122.4194,
        photos=["photo1.jpg", "photo2.jpg"]
    )
    
    # Create investment assumptions
    assumptions = InvestmentAssumptions(
        equity_percentage=20,
        cash_reserves=10000,
        amortization_period=30,
        interest_rate=0.045,
        renovation_budget=0,
        extra_cash_reserves=5000,
        rental_growth_rate=0.02,
        expense_growth_rate=0.02,
        vacancy_rate=0.05,
        property_mgmt_rate=0.10,
        maintenance_rate=0.05
    )
    
    # Create comparable properties
    comparable_properties = [
        PropertyDetails(
            zpid=str(i),
            address=f"{i} Similar St, Anytown, USA",
            price=500000 + (i * 10000),
            bedrooms=3,
            bathrooms=2,
            square_feet=2000 + (i * 100),
            year_built=2000,
            property_type="Single Family",
            rent_estimate=2500 + (i * 100)
        ) for i in range(1, 6)
    ]
    
    # Initialize analyzers
    financial_analyzer = FinancialAnalyzer(
        property_details=property_details,
        investment_assumptions=assumptions,
        comparable_properties=comparable_properties
    )
    
    # Perform analysis
    analysis_results = financial_analyzer.analyze(project_life=5)
    
    # Calculate advanced metrics
    advanced_calculator = AdvancedMetricsCalculator(
        property_price=property_details.price,
        monthly_rent=property_details.rent_estimate,
        operating_expenses=analysis_results.analysis_results.operating_expenses
    )
    
    tax_metrics = advanced_calculator.calculate_tax_metrics()
    sensitivity_metrics = advanced_calculator.calculate_sensitivity()
    scenario_metrics = advanced_calculator.calculate_scenarios()
    
    # Print summary
    print("\nInvestment Analysis Summary")
    print("-" * 50)
    print(f"Property: {property_details.address}")
    print(f"Price: ${property_details.price:,.2f}")
    print(f"Monthly Rent: ${property_details.rent_estimate:,.2f}")
    
    print("\nKey Metrics:")
    print(f"Cap Rate: {analysis_results.financial_metrics.cap_rate:.1f}%")
    print(f"Cash on Cash Return: {analysis_results.financial_metrics.cash_on_cash_return:.1f}%")
    print(f"IRR (5yr): {analysis_results.financial_metrics.irr:.1f}%")
    print(f"Total ROI (5yr): {analysis_results.financial_metrics.total_roi:.1f}%")
    
    print("\nRisk Metrics:")
    print(f"Default Risk Score: {analysis_results.financial_metrics.default_risk_score:.0f}/100")
    print(f"Debt Coverage Ratio: {analysis_results.financial_metrics.debt_coverage_ratio:.2f}")
    print(f"Break Even Ratio: {analysis_results.financial_metrics.break_even_ratio:.2f}")
    
    print("\nTax Benefits:")
    print(f"Annual Depreciation: ${tax_metrics.depreciation_annual:,.2f}")
    print(f"Annual Tax Savings: ${tax_metrics.tax_savings_annual:,.2f}")
    
    print("\nScenario Analysis:")
    print(f"Best Case Return: {scenario_metrics.best_case['Total_Return']*100:.1f}%")
    print(f"Expected Return: {scenario_metrics.expected_case['Total_Return']*100:.1f}%")
    print(f"Worst Case Return: {scenario_metrics.worst_case['Total_Return']*100:.1f}%")
    
    # Generate report
    report_path = Path("reports") / f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    report_path.parent.mkdir(exist_ok=True)
    
    report_generator = ReportGenerator(analysis_results)
    report_generator.generate_html_report(report_path)
    print(f"\nDetailed report generated at: {report_path}")

if __name__ == "__main__":
    main()
