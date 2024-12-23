import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.data import MarketDataLoader
from src.analysis import AnalysisManager
from src.utils import FormatHelper, TimeHelper

# Page configuration
st.set_page_config(
    page_title="Investment Analysis - Home",
    page_icon="🏠",
    layout="wide"
)

class HomePage:
    def __init__(self):
        self.market_data = MarketDataLoader()
        self.analysis = AnalysisManager()
        self.format = FormatHelper()
        
    def run(self):
        # Sidebar
        with st.sidebar:
            self.render_sidebar()
        
        # Main content
        st.title("Investment Analysis Dashboard")
        
        # Get ticker from session state or default
        ticker = st.session_state.get('ticker', 'AAPL')
        
        # Market Overview
        self.render_market_overview(ticker)
        
        # Analysis Summary
        self.render_analysis_summary(ticker)
        
        # Recent News
        self.render_recent_news(ticker)
    
    def render_sidebar(self):
        st.title("Settings")
        
        # Ticker input
        ticker = st.text_input(
            "Enter Ticker",
            value=st.session_state.get('ticker', 'AAPL')
        ).upper()
        
        if ticker != st.session_state.get('ticker'):
            st.session_state.ticker = ticker
            st.experimental_rerun()
        
        # Time period selector
        st.selectbox(
            "Time Period",
            options=['1D', '1W', '1M', '3M', '1Y', '5Y'],
            key='timeperiod'
        )
        
        # Analysis options
        st.divider()
        st.markdown("### Analysis Options")
        
        st.checkbox("Technical Analysis", value=True, key='show_technical')
        st.checkbox("Fundamental Analysis", value=True, key='show_fundamental')
        st.checkbox("Risk Metrics", value=True, key='show_risk')
        st.checkbox("Sentiment Analysis", value=True, key='show_sentiment')
    
    def render_market_overview(self, ticker):
        st.header("Market Overview")
        
        try:
            # Get market data
            data = self.market_data.get_market_data(ticker, '1d')
            
            # Create columns for metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                self.metric_card(
                    "Current Price",
                    self.format.format_currency(data['Close'].iloc[-1]),
                    f"{data['Close'].pct_change().iloc[-1]:.2%}"
                )
                
            with col2:
                self.metric_card(
                    "Volume",
                    self.format.format_large_number(data['Volume'].iloc[-1]),
                    f"{data['Volume'].pct_change().iloc[-1]:.2%}"
                )
                
            with col3:
                self.metric_card(
                    "Day Range",
                    f"{self.format.format_currency(data['Low'].iloc[-1])} - "
                    f"{self.format.format_currency(data['High'].iloc[-1])}"
                )
                
            with col4:
                market_status = "Open" if TimeHelper.is_market_open() else "Closed"
                self.metric_card("Market Status", market_status)
            
            # Price chart
            st.plotly_chart(
                self.market_data.create_price_chart(data),
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"Error loading market data: {str(e)}")
    
    def render_analysis_summary(self, ticker):
        st.header("Analysis Summary")
        
        try:
            # Get analysis results
            analysis = self.analysis.perform_complete_analysis(
                ticker,
                self.market_data.get_market_data(ticker, '1y'),
                [],  # news data
                {}   # financial reports
            )
            
            # Create columns for different analyses
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.session_state.show_technical:
                    st.subheader("Technical Analysis")
                    signals = analysis['technical']['signals']
                    for signal, value in signals.items():
                        st.info(f"{signal}: {value}")
            
            with col2:
                if st.session_state.show_fundamental:
                    st.subheader("Fundamental Analysis")
                    metrics = analysis['fundamental']['profitability']
                    for metric, value in metrics.items():
                        st.metric(metric, f"{value:.2%}")
            
            with col3:
                if st.session_state.show_risk:
                    st.subheader("Risk Metrics")
                    risk = analysis['risk']
                    for metric, value in risk.items():
                        if isinstance(value, dict):
                            continue
                        st.metric(metric, f"{value:.2f}")
            
        except Exception as e:
            st.error(f"Error loading analysis: {str(e)}")
    
    def render_recent_news(self, ticker):
        st.header("Recent News")
        
        try:
            news = self.market_data.get_company_news(ticker)
            
            for article in news[:5]:  # Show 5 most recent articles
                with st.expander(article['title']):
                    st.write(article['description'])
                    st.caption(
                        f"Source: {article['source']} | "
                        f"Published: {article['published_at']}"
                    )
                    if article.get('sentiment'):
                        sentiment = article['sentiment']
                        st.progress(
                            (sentiment + 1) / 2,  # Convert -1 to 1 to 0 to 1
                            text=f"Sentiment: {sentiment:.2f}"
                        )
        
        except Exception as e:
            st.error(f"Error loading news: {str(e)}")
    
    @staticmethod
    def metric_card(label, value, delta=None):
        if delta:
            st.metric(label, value, delta)
        else:
            st.metric(label, value)

if __name__ == "__main__":
    home_page = HomePage()
    home_page.run()