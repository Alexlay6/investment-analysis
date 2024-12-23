import streamlit as st
import pandas as pd
from src.data import MarketDataLoader
from src.analysis import TechnicalAnalyzer
from src.utils import VisualizationHelper
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Technical Analysis",
    page_icon="📈",
    layout="wide"
)

class TechnicalPage:
    def __init__(self):
        self.market_data = MarketDataLoader()
        self.analyzer = TechnicalAnalyzer()
        self.viz = VisualizationHelper()
        
    def run(self):
        st.title("Technical Analysis")
        
        # Sidebar controls
        with st.sidebar:
            self.render_sidebar()
        
        # Get data
        ticker = st.session_state.get('ticker', 'AAPL')
        period = st.session_state.get('timeperiod', '1y')
        data = self.market_data.get_market_data(ticker, period)
        
        # Main chart
        self.render_main_chart(data)
        
        # Technical indicators
        self.render_technical_indicators(data)
        
        # Pattern analysis
        self.render_pattern_analysis(data)
        
        # Support/Resistance levels
        self.render_support_resistance(data)
    
    def render_sidebar(self):
        st.title("Analysis Settings")
        
        # Indicator selection
        st.subheader("Select Indicators")
        
        # Moving Averages
        st.markdown("#### Moving Averages")
        st.checkbox("SMA 20", value=True, key='sma_20')
        st.checkbox("SMA 50", value=True, key='sma_50')
        st.checkbox("SMA 200", value=True, key='sma_200')
        st.checkbox("EMA 20", value=False, key='ema_20')
        
        # Oscillators
        st.markdown("#### Oscillators")
        st.checkbox("RSI", value=True, key='show_rsi')
        st.checkbox("MACD", value=True, key='show_macd')
        st.checkbox("Stochastic", value=False, key='show_stoch')
        
        # Volume Analysis
        st.markdown("#### Volume")
        st.checkbox("Volume", value=True, key='show_volume')
        st.checkbox("OBV", value=False, key='show_obv')
        
        # Pattern Recognition
        st.markdown("#### Patterns")
        st.checkbox("Candlestick Patterns", value=True, key='show_patterns')
        st.checkbox("Support/Resistance", value=True, key='show_sr')
    
    def render_main_chart(self, data):
        st.header("Price Chart")
        
        # Create figure with secondary y-axis
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3]
        )
        
        # Add candlestick
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='OHLC'
            ),
            row=1, col=1
        )
        
        # Add Moving Averages
        if st.session_state.sma_20:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['Close'].rolling(20).mean(),
                    name='SMA 20',
                    line=dict(color='blue', width=1)
                ),
                row=1, col=1
            )
        
        if st.session_state.sma_50:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['Close'].rolling(50).mean(),
                    name='SMA 50',
                    line=dict(color='orange', width=1)
                ),
                row=1, col=1
            )
        
        # Add volume bars
        if st.session_state.show_volume:
            colors = ['red' if row['Open'] > row['Close'] else 'green' 
                     for idx, row in data.iterrows()]
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data['Volume'],
                    name='Volume',
                    marker_color=colors
                ),
                row=2, col=1
            )
        
        # Update layout
        fig.update_layout(
            height=800,
            xaxis_rangeslider_visible=False,
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_technical_indicators(self, data):
        st.header("Technical Indicators")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.show_rsi:
                self.render_rsi_chart(data)
            
            if st.session_state.show_stoch:
                self.render_stochastic_chart(data)
        
        with col2:
            if st.session_state.show_macd:
                self.render_macd_chart(data)
            
            if st.session_state.show_obv:
                self.render_obv_chart(data)
    
    def render_pattern_analysis(self, data):
        if st.session_state.show_patterns:
            st.header("Pattern Analysis")
            
            # Get pattern analysis
            patterns = self.analyzer._identify_patterns(
                data['High'].values,
                data['Low'].values,
                data['Close'].values
            )
            
            if patterns:
                for pattern in patterns:
                    st.info(f"Detected Pattern: {pattern}")
            else:
                st.write("No significant patterns detected in the current timeframe.")
    
    def render_support_resistance(self, data):
        if st.session_state.show_sr:
            st.header("Support & Resistance Levels")
            
            # Get S/R levels
            levels = self.analyzer._find_support_resistance(data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Support Levels")
                for level in levels['support']:
                    st.write(f"${level:.2f}")
            
            with col2:
                st.subheader("Resistance Levels")
                for level in levels['resistance']:
                    st.write(f"${level:.2f}")
    
    def render_rsi_chart(self, data):
        """Render RSI chart."""
        fig = go.Figure()
        
        rsi = self.analyzer._calculate_rsi(data['Close'])
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=rsi,
                name='RSI'
            )
        )
        
        # Add overbought/oversold lines
        fig.add_hline(y=70, line_dash="dash", line_color="red")
        fig.add_hline(y=30, line_dash="dash", line_color="green")
        
        fig.update_layout(
            title="Relative Strength Index (RSI)",
            height=300,
            yaxis_title="RSI",
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_macd_chart(self, data):
        """Render MACD chart."""
        fig = go.Figure()
        
        macd = self.analyzer._calculate_macd(data['Close'])
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=macd['macd'],
                name='MACD'
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=macd['signal'],
                name='Signal'
            )
        )
        
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=macd['hist'],
                name='Histogram'
            )
        )
        
        fig.update_layout(
            title="MACD",
            height=300,
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    technical_page = TechnicalPage()
    technical_page.run()