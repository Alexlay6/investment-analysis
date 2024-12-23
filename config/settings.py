from pydantic_settings import BaseSettings
from typing import Dict, Any
import streamlit as st

class Settings(BaseSettings):
    # Data update intervals (in seconds)
    MARKET_DATA_UPDATE_INTERVAL: int = 60
    TECHNICAL_UPDATE_INTERVAL: int = 300
    FUNDAMENTAL_UPDATE_INTERVAL: int = 3600
    NEWS_UPDATE_INTERVAL: int = 300

    # Technical Analysis Settings
    TECHNICAL_INDICATORS: Dict[str, Any] = {
        'moving_averages': [20, 50, 200],
        'rsi': {'period': 14, 'overbought': 70, 'oversold': 30},
        'macd': {'fast': 12, 'slow': 26, 'signal': 9},
        'bollinger_bands': {'period': 20, 'std_dev': 2}
    }

    # Fundamental Analysis Settings
    FUNDAMENTAL_METRICS: Dict[str, Any] = {
        'growth_metrics': ['Revenue', 'EBITDA', 'Net Income'],
        'valuation_metrics': ['P/E', 'EV/EBITDA', 'P/B'],
        'profitability_metrics': ['Gross Margin', 'Operating Margin', 'Net Margin'],
        'liquidity_metrics': ['Current Ratio', 'Quick Ratio', 'Cash Ratio']
    }

    # Risk Analysis Settings
    RISK_METRICS: Dict[str, Any] = {
        'var_confidence_level': 0.95,
        'var_time_horizon': 10,
        'correlation_lookback': 252,
        'volatility_window': 252
    }

    # Sentiment Analysis Settings
    SENTIMENT_SETTINGS: Dict[str, Any] = {
        'news_lookback_days': 30,
        'min_article_length': 100,
        'sentiment_thresholds': {
            'very_positive': 0.6,
            'positive': 0.2,
            'neutral': -0.2,
            'negative': -0.6
        }
    }

    # Cache Settings
    CACHE_SETTINGS: Dict[str, Any] = {
        'market_data_ttl': 3600,
        'technical_analysis_ttl': 3600,
        'fundamental_analysis_ttl': 86400,
        'news_ttl': 3600
    }

    # API Rate Limits (requests per minute)
    RATE_LIMITS: Dict[str, int] = {
        'finnhub': 60,
        'polygon': 5,
        'alpha_vantage': 5,
        'news_api': 10
    }

    class Config:
        env_file = '.env'
        case_sensitive = True

    @property
    def api_keys(self) -> Dict[str, str]:
        """Get API keys from Streamlit secrets."""
        return {
            'anthropic': st.secrets['ANTHROPIC_API_KEY'],
            'finnhub': st.secrets['FINNHUB_API_KEY'],
            'polygon': st.secrets['POLYGON_API_KEY'],
            'alpha_vantage': st.secrets['ALPHA_VANTAGE_API_KEY'],
            'news_api': st.secrets['NEWS_API_KEY']
        }

    def get_indicator_settings(self, indicator: str) -> Dict[str, Any]:
        """Get settings for specific technical indicator."""
        return self.TECHNICAL_INDICATORS.get(indicator, {})

    def get_cache_ttl(self, data_type: str) -> int:
        """Get cache TTL for specific data type."""
        return self.CACHE_SETTINGS.get(f'{data_type}_ttl', 3600)

    def get_rate_limit(self, api: str) -> int:
        """Get rate limit for specific API."""
        return self.RATE_LIMITS.get(api, 1)