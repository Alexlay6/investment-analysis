import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.data import MarketDataLoader
from src.analysis import RiskAnalyzer
from src.utils import FormatHelper

# Page configuration
st.set_page_config(
    page_title="Risk Analysis",
    page_icon="⚠️",
    layout="wide"
)

class RiskPage:
    def __init__(self):
        self.market_data = MarketDataLoader()
        self.analyzer = RiskAnalyzer()
        self.format = FormatHelper()
        
    def run(self):
        st.title("Risk Analysis")
        
        # Sidebar controls
        with st.sidebar:
            self.render_sidebar()
        
        # Get data
        ticker = st.session_state.get('ticker', 'AAPL')
        period = st.session_state.get('timeperiod', '1y')
        
        try:
            # Get market data
            data = self.market_data.get_market_data(ticker, period)
            
            # Calculate risk metrics
            risk_metrics = self.analyzer.calculate_risk_metrics(data)
            
            # Render different sections
            self.render_risk_overview(risk_metrics)
            self.render_volatility_analysis(data, risk_metrics)
            self.render_var_analysis(risk_metrics)
            self.render_correlation_analysis(data)
            self.render_risk_alerts(risk_metrics)
            
        except Exception as e:
            st.error(f"Error analyzing risk metrics: {str(e)}")
    
    def render_sidebar(self):
        st.title("Risk Settings")
        
        # VaR settings
        st.subheader("Value at Risk")
        st.slider(
            "Confidence Level",
            min_value=0.90,
            max_value=0.99,
            value=0.95,
            step=0.01,
            key='var_confidence'
        )
        
        # Volatility settings
        st.subheader("Volatility")
        st.selectbox(
            "Calculation Method",
            options=['Historical', 'EWMA', 'GARCH'],
            key='vol_method'
        )
        
        # Correlation settings
        st.subheader("Correlation Analysis")
        st.multiselect(
            "Compare with",
            options=['SPY', 'QQQ', 'IWM', 'VIX'],
            default=['SPY'],
            key='correlation_assets'
        )
        
        # Risk alert settings
        st.subheader("Risk Alerts")
        st.number_input(
            "Volatility Alert Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.05,
            key='vol_threshold'
        )
    
    def render_risk_overview(self, risk_metrics):
        st.header("Risk Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            vol = risk_metrics['volatility']
            st.metric(
                "Annual Volatility",
                f"{vol['annual_volatility']*100:.2f}%",
                delta=f"{(vol['current_rolling_vol']-vol['annual_volatility'])*100:.2f}%"
            )
        
        with col2:
            var = risk_metrics['value_at_risk']
            st.metric(
                "Value at Risk (95%)",
                f"{abs(var['historical_var'])*100:.2f}%"
            )
        
        with col3:
            beta = risk_metrics['beta']
            st.metric(
                "Beta",
                f"{beta['beta']:.2f}",
                delta=f"R²: {beta['r_squared']:.2f}"
            )
        
        with col4:
            drawdown = risk_metrics['drawdown']
            st.metric(
                "Maximum Drawdown",
                f"{abs(drawdown['max_drawdown'])*100:.2f}%"
            )
    
    def render_volatility_analysis(self, data, risk_metrics):
        st.header("Volatility Analysis")
        
        # Create returns series
        returns = data['Close'].pct_change().dropna()
        
        # Create figure with two subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Returns Distribution", "Rolling Volatility"),
            vertical_spacing=0.15
        )
        
        # Returns distribution
        fig.add_trace(
            go.Histogram(
                x=returns,
                name="Returns",
                nbinsx=50,
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Rolling volatility
        rolling_vol = returns.rolling(window=30).std() * np.sqrt(252)
        fig.add_trace(
            go.Scatter(
                x=rolling_vol.index,
                y=rolling_vol,
                name="30-Day Volatility"
            ),
            row=2, col=1
        )
        
        fig.update_layout(height=600, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)
        
        # Additional volatility metrics
        with st.expander("Detailed Volatility Metrics"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("Historical Volatility Metrics:")
                volatility = risk_metrics['volatility']
                for metric, value in volatility.items():
                    if isinstance(value, (int, float)):
                        st.write(f"{metric}: {value*100:.2f}%")
            
            with col2:
                st.write("Forward Volatility Estimate:")
                st.write(f"{volatility.get('forward_vol_estimate', 0)*100:.2f}%")
    
    def render_var_analysis(self, risk_metrics):
        st.header("Value at Risk (VaR) Analysis")
        
        var = risk_metrics['value_at_risk']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # VaR metrics
            st.subheader("VaR Metrics")
            st.metric(
                "Historical VaR",
                f"{abs(var['historical_var'])*100:.2f}%"
            )
            st.metric(
                "Parametric VaR",
                f"{abs(var['parametric_var'])*100:.2f}%"
            )
            st.metric(
                "Conditional VaR",
                f"{abs(var['conditional_var'])*100:.2f}%"
            )
        
        with col2:
            # VaR visualization
            fig = go.Figure()
            
            methods = ['Historical', 'Parametric', 'Conditional']
            values = [
                var['historical_var'],
                var['parametric_var'],
                var['conditional_var']
            ]
            
            fig.add_trace(
                go.Bar(
                    x=methods,
                    y=[abs(v)*100 for v in values],
                    name='VaR'
                )
            )
            
            fig.update_layout(
                title="VaR Comparison",
                yaxis_title="VaR (%)",
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def render_correlation_analysis(self, data):
        st.header("Correlation Analysis")
        
        # Get correlation assets
        correlation_assets = st.session_state.correlation_assets
        
        if correlation_assets:
            # Calculate correlations
            correlations = self.analyzer.calculate_correlations(
                data,
                correlation_assets
            )
            
            # Create heatmap
            fig = go.Figure(
                data=go.Heatmap(
                    z=correlations.values,
                    x=correlations.columns,
                    y=correlations.index,
                    colorscale='RdBu',
                    zmin=-1,
                    zmax=1
                )
            )
            
            fig.update_layout(
                title="Correlation Matrix",
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def render_risk_alerts(self, risk_metrics):
        st.header("Risk Alerts")
        
        # Check volatility threshold
        vol_threshold = st.session_state.vol_threshold
        current_vol = risk_metrics['volatility']['current_rolling_vol']
        
        if current_vol > vol_threshold:
            st.warning(
                f"⚠️ Current volatility ({current_vol*100:.2f}%) is above "
                f"threshold ({vol_threshold*100:.2f}%)"
            )
        
        # Check VaR threshold
        var = risk_metrics['value_at_risk']['historical_var']
        if abs(var) > 0.05:  # 5% VaR threshold
            st.warning(
                f"⚠️ Value at Risk ({abs(var)*100:.2f}%) indicates "
                "significant potential losses"
            )
        
        # Check correlation risks
        beta = risk_metrics['beta']['beta']
        if beta > 1.5:
            st.warning(
                f"⚠️ High market sensitivity (Beta: {beta:.2f}) indicates "
                "increased market risk"
            )
        
        # Check drawdown
        max_drawdown = risk_metrics['drawdown']['max_drawdown']
        if abs(max_drawdown) > 0.2:  # 20% drawdown threshold
            st.warning(
                f"⚠️ Large maximum drawdown ({abs(max_drawdown)*100:.2f}%) "
                "indicates significant downside risk"
            )

if __name__ == "__main__":
    risk_page = RiskPage()
    risk_page.run()