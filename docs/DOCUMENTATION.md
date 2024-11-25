# Real Estate Investment Analyzer Documentation

## Overview

The Real Estate Investment Analyzer is a comprehensive tool for analyzing real estate investment opportunities. It provides detailed financial analysis, market comparisons, risk assessment, and beautiful interactive reports.

## Key Features

- Comprehensive property analysis
- Advanced financial metrics
- Market comparison
- Risk assessment
- Tax analysis
- Sensitivity analysis
- Scenario analysis
- Interactive HTML reports

## Components

### 1. Property Analysis (`src/utils/analysis.py`)

The `PropertyAnalyzer` class provides core property analysis functionality:

```python
analyzer = PropertyAnalyzer(property_details, investment_assumptions)
results = analyzer.analyze(project_life=5)
```

Key features:
- Cash flow calculations
- Operating expense analysis
- Rent estimation
- Value projection

### 2. Market Analysis (`src/utils/market_analysis.py`)

The `MarketAnalyzer` class handles market trends and comparisons:

```python
analyzer = MarketAnalyzer(comparable_properties)
metrics = analyzer.calculate_market_metrics()
position = analyzer.analyze_property_position(property)
```

Key features:
- Market metrics calculation
- Property position analysis
- Similar property finder
- Market visualization

### 3. Financial Analysis (`src/analysis/financial_analyzer.py`)

The `FinancialAnalyzer` class combines property and market analysis:

```python
analyzer = FinancialAnalyzer(property_details, assumptions, comparable_properties)
analysis = analyzer.analyze(project_life=5)
```

Key metrics:
- Cap Rate
- Cash on Cash Return
- IRR
- NPV
- Debt Coverage Ratio
- Break Even Ratio
- Default Risk Score

### 4. Advanced Metrics (`src/analysis/advanced_metrics.py`)

The `AdvancedMetricsCalculator` provides additional analysis:

```python
calculator = AdvancedMetricsCalculator(price, rent, operating_expenses)
tax_metrics = calculator.calculate_tax_metrics()
sensitivity = calculator.calculate_sensitivity()
scenarios = calculator.calculate_scenarios()
```

Features:
- Tax analysis
- Sensitivity analysis
- Scenario analysis
- Risk metrics

### 5. Report Generation (`src/analysis/report_generator.py`)

The `ReportGenerator` creates beautiful HTML reports:

```python
generator = ReportGenerator(analysis_results)
generator.generate_html_report(output_path)
```

Report sections:
- Property Overview
- Financial Summary
- Investment Analysis
- Market Analysis
- Risk Analysis

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/real-estate-analyzer.git
cd real-estate-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage Example

```python
from src.models.property import PropertyDetails
from src.models.investment import InvestmentAssumptions
from src.analysis.financial_analyzer import FinancialAnalyzer
from src.analysis.report_generator import ReportGenerator

# Create property details
property_details = PropertyDetails(
    address="123 Main St",
    price=500000,
    bedrooms=3,
    bathrooms=2,
    square_feet=2000
)

# Create investment assumptions
assumptions = InvestmentAssumptions(
    equity_percentage=20,
    interest_rate=0.045,
    amortization_period=30
)

# Perform analysis
analyzer = FinancialAnalyzer(property_details, assumptions)
results = analyzer.analyze()

# Generate report
generator = ReportGenerator(results)
generator.generate_html_report("report.html")
```

## Testing

Run the test suite:
```bash
python -m unittest discover tests
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
