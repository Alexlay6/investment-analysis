# Investment Analysis Dashboard

A comprehensive financial analysis system built with Streamlit, providing real-time market data, technical analysis, fundamental analysis, and AI-powered insights.

## Features

- Real-time market data tracking
- Technical analysis with multiple indicators
- Fundamental analysis using financial statements
- Sentiment analysis using news and social media
- Risk metrics and portfolio analysis
- Stock screening capabilities

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/investment-analysis.git
cd investment-analysis
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. Run the dashboard:
```bash
streamlit run src/pages/00_🏠_Home.py
```

## API Keys Required

- Anthropic (Claude AI)
- Finnhub
- Polygon.io
- Alpha Vantage
- News API

## Project Structure

```
investment-analysis/
├── src/
│   ├── data/         # Data collection modules
│   ├── analysis/     # Analysis modules
│   ├── utils/        # Utility functions
│   └── pages/        # Streamlit pages
```

## Pages

1. 🏠 Home: Overview dashboard
2. 📈 Technical: Technical analysis
3. 📊 Fundamental: Fundamental analysis
4. ⚠️ Risk: Risk metrics
5. 📰 News: News and sentiment
6. 🔍 Screening: Stock screening

## Usage

### Market Data
```python
from src.data.market_data import MarketDataLoader

# Initialize loader
loader = MarketDataLoader()

# Get market data
data = loader.get_market_data("AAPL", "1y")
```

### Technical Analysis
```python
from src.analysis.technical import TechnicalAnalyzer

# Initialize analyzer
analyzer = TechnicalAnalyzer()

# Get analysis
analysis = analyzer.analyze_price_action(data)
```

### Fundamental Analysis
```python
from src.analysis.fundamental import FundamentalAnalyzer

# Initialize analyzer
analyzer = FundamentalAnalyzer()

# Get analysis
analysis = analyzer.analyze_company("AAPL")
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.