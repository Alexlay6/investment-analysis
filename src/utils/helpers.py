import pandas as pd
import numpy as np
from typing import Dict, Any, List, Union
import streamlit as st
from datetime import datetime, timedelta
import pytz

class DataProcessing:
    """Helper functions for data processing."""
    
    @staticmethod
    def clean_financials(df: pd.DataFrame) -> pd.DataFrame:
        """Clean financial data."""
        # Convert to numeric
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # Fill missing values
        df.fillna(method='ffill', inplace=True)
        df.fillna(0, inplace=True)
        
        return df

    @staticmethod
    def calculate_returns(prices: pd.Series) -> pd.Series:
        """Calculate return series."""
        return prices.pct_change().fillna(0)

    @staticmethod
    def calculate_log_returns(prices: pd.Series) -> pd.Series:
        """Calculate logarithmic returns."""
        return np.log(prices / prices.shift(1)).fillna(0)

    @staticmethod
    def normalize_series(series: pd.Series) -> pd.Series:
        """Normalize series to 0-1 range."""
        return (series - series.min()) / (series.max() - series.min())

class FormatHelper:
    """Helper functions for formatting data."""
    
    @staticmethod
    def format_currency(value: float) -> str:
        """Format currency values."""
        if abs(value) >= 1e9:
            return f"${value/1e9:.1f}B"
        elif abs(value) >= 1e6:
            return f"${value/1e6:.1f}M"
        elif abs(value) >= 1e3:
            return f"${value/1e3:.1f}K"
        return f"${value:.2f}"

    @staticmethod
    def format_percentage(value: float) -> str:
        """Format percentage values."""
        return f"{value:.2f}%"

    @staticmethod
    def format_large_number(value: float) -> str:
        """Format large numbers."""
        if abs(value) >= 1e9:
            return f"{value/1e9:.1f}B"
        elif abs(value) >= 1e6:
            return f"{value/1e6:.1f}M"
        elif abs(value) >= 1e3:
            return f"{value/1e3:.1f}K"
        return f"{value:.0f}"

class TimeHelper:
    """Helper functions for time-related operations."""
    
    @staticmethod
    def get_market_hours() -> Dict[str, datetime]:
        """Get market hours in EST."""
        est = pytz.timezone('US/Eastern')
        now = datetime.now(est)
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        return {
            'market_open': market_open,
            'market_close': market_close,
            'current_time': now
        }

    @staticmethod
    def is_market_open() -> bool:
        """Check if market is currently open."""
        hours = TimeHelper.get_market_hours()
        current = hours['current_time']
        
        # Check if it's a weekday
        if current.weekday() >= 5:
            return False
            
        return hours['market_open'] <= current <= hours['market_close']

    @staticmethod
    def time_to_market_close() -> timedelta:
        """Get time remaining until market close."""
        hours = TimeHelper.get_market_hours()
        if TimeHelper.is_market_open():
            return hours['market_close'] - hours['current_time']
        return timedelta(0)

class ValidationHelper:
    """Helper functions for data validation."""
    
    @staticmethod
    def validate_ticker(ticker: str) -> bool:
        """Validate ticker symbol."""
        if not ticker:
            return False
        return bool(ticker.strip().upper())

    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
        """Validate date range."""
        if not start_date or not end_date:
            return False
        return start_date < end_date

    @staticmethod
    def validate_numerical(value: Any) -> bool:
        """Validate numerical value."""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

class VisualizationHelper:
    """Helper functions for data visualization."""
    
    @staticmethod
    def get_color_scheme() -> Dict[str, str]:
        """Get consistent color scheme."""
        return {
            'up': '#00C805',
            'down': '#FF3B69',
            'neutral': '#888888',
            'primary': '#1F77B4',
            'secondary': '#FF7F0E'
        }

    @staticmethod
    def get_timeframe_options() -> List[Dict[str, str]]:
        """Get standard timeframe options."""
        return [
            {'label': '1D', 'value': '1d'},
            {'label': '1W', 'value': '1wk'},
            {'label': '1M', 'value': '1mo'},
            {'label': '3M', 'value': '3mo'},
            {'label': '1Y', 'value': '1y'},
            {'label': '5Y', 'value': '5y'}
        ]

    @staticmethod
    def create_candlestick_figure(data: pd.DataFrame, 
                                include_volume: bool = True) -> Dict[str, Any]:
        """Create standard candlestick chart configuration."""
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        # Candlestick
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='OHLC'
        ))
        
        # Volume
        if include_volume and 'Volume' in data.columns:
            fig.add_trace(go.Bar(
                x=data.index,
                y=data['Volume'],
                name='Volume',
                yaxis='y2'
            ))
            
            fig.update_layout(
                yaxis2=dict(
                    title='Volume',
                    overlaying='y',
                    side='right'
                )
            )
        
        fig.update_layout(
            height=600,
            xaxis_rangeslider_visible=False,
            template='plotly_white'
        )
        
        return fig