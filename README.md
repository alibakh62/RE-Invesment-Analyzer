# Real Estate Investment Analyzer

A powerful Python-based tool for analyzing real estate investment opportunities. This tool provides comprehensive financial analysis, market comparisons, risk assessment, and generates beautiful interactive reports.

## Features

- 📊 Comprehensive property analysis
- 💰 Advanced financial metrics
- 🏘️ Market comparison with similar properties
- 📈 Risk assessment and scoring
- 📑 Tax analysis and benefits
- 🔄 Sensitivity and scenario analysis
- 📱 Interactive HTML reports

## Architecture

The codebase is organized into several key modules:

### Core Modules

1. **Property Analysis** (`src/utils/analysis.py`)
   - Handles core property calculations
   - Cash flow analysis
   - Operating expense calculations
   - Value projections

2. **Market Analysis** (`src/utils/market_analysis.py`)
   - Market trends and metrics
   - Comparable property analysis
   - Market position assessment
   - Price and rent comparisons

3. **Financial Analysis** (`src/analysis/financial_analyzer.py`)
   - Combines property and market analysis
   - Advanced financial metrics
   - Risk assessment
   - Investment performance metrics

### Advanced Features

4. **Advanced Metrics** (`src/analysis/advanced_metrics.py`)
   - Tax analysis and benefits
   - Sensitivity analysis
   - Scenario modeling
   - Risk metrics

5. **Report Generation** (`src/analysis/report_generator.py`)
   - Interactive HTML reports
   - Beautiful visualizations
   - Comprehensive analysis presentation

### Data Models

6. **Property Model** (`src/models/property.py`)
   - Property details and characteristics
   - Location information
   - Historical data

7. **Investment Model** (`src/models/investment.py`)
   - Investment assumptions
   - Financing details
   - Growth projections

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/RE-Investment-Analyzer.git
cd RE-Investment-Analyzer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

1. Create a property analysis:
```python
from src.models.property import PropertyDetails
from src.models.investment import InvestmentAssumptions
from src.analysis.financial_analyzer import FinancialAnalyzer

# Create property details
property = PropertyDetails(
    address="123 Main St",
    price=500000,
    bedrooms=3,
    bathrooms=2,
    square_feet=2000
)

# Set investment assumptions
assumptions = InvestmentAssumptions(
    equity_percentage=20,
    interest_rate=0.045,
    amortization_period=30
)

# Run analysis
analyzer = FinancialAnalyzer(property, assumptions)
results = analyzer.analyze()
```

2. Generate a report:
```python
from src.analysis.report_generator import ReportGenerator

# Create and save report
generator = ReportGenerator(results)
generator.generate_html_report("report.html")
```

## Development

### Running Tests
```bash
python -m unittest discover tests
```

### Project Structure
```
RE-Investment-Analyzer/
├── src/
│   ├── models/          # Data models
│   ├── utils/           # Core utilities
│   └── analysis/        # Analysis modules
├── tests/               # Unit tests
├── docs/               # Documentation
├── examples/           # Example code
└── reports/            # Generated reports
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Python 3.8+
- Uses Plotly for beautiful visualizations
- Pandas for data analysis
- NumPy for numerical computations