import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.data import FinancialDataLoader
from src.analysis import FundamentalAnalyzer
from src.utils import FormatHelper

# Page configuration
st.set_page_config(
    page_title="Fundamental Analysis",
    page_icon="📊",
    layout="wide"
)

class FundamentalPage:
    def __init__(self):
        self.financial_data = FinancialDataLoader()
        self.analyzer = FundamentalAnalyzer()
        self.format = FormatHelper()
        
    def run(self):
        st.title("Fundamental Analysis")
        
        # Sidebar controls
        with st.sidebar:
            self.render_sidebar()
        
        # Get data
        ticker = st.session_state.get('ticker', 'AAPL')
        
        try:
            # Get financial data and analysis
            financials = self.financial_data.get_financial_statements(ticker)
            analysis = self.analyzer.analyze_company(ticker)
            
            # Render different sections
            self.render_company_overview(financials['info'])
            self.render_key_metrics(analysis)
            self.render_financial_statements(financials)
            self.render_ratio_analysis(analysis)
            self.render_growth_analysis(analysis)
            self.render_valuation_analysis(analysis)
            
        except Exception as e:
            st.error(f"Error loading fundamental data: {str(e)}")
    
    def render_sidebar(self):
        st.title("Analysis Settings")
        
        # Statement selection
        st.subheader("Financial Statements")
        st.checkbox("Income Statement", value=True, key='show_income')
        st.checkbox("Balance Sheet", value=True, key='show_balance')
        st.checkbox("Cash Flow", value=True, key='show_cashflow')
        
        # Ratio selection
        st.subheader("Ratio Analysis")
        st.checkbox("Profitability", value=True, key='show_profitability')
        st.checkbox("Liquidity", value=True, key='show_liquidity')
        st.checkbox("Solvency", value=True, key='show_solvency')
        st.checkbox("Efficiency", value=True, key='show_efficiency')
        
        # Comparison settings
        st.subheader("Comparison")
        st.multiselect(
            "Compare with",
            options=['Industry Average', 'Sector Average', 'S&P 500'],
            default=['Industry Average'],
            key='comparisons'
        )
    
    def render_company_overview(self, info):
        st.header("Company Overview")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Market Cap",
                self.format.format_currency(info.get('marketCap', 0))
            )
            st.metric(
                "Sector",
                info.get('sector', 'N/A')
            )
        
        with col2:
            st.metric(
                "P/E Ratio",
                f"{info.get('trailingPE', 0):.2f}"
            )
            st.metric(
                "Industry",
                info.get('industry', 'N/A')
            )
        
        with col3:
            st.metric(
                "Dividend Yield",
                f"{info.get('dividendYield', 0)*100:.2f}%"
            )
            st.metric(
                "Beta",
                f"{info.get('beta', 0):.2f}"
            )
        
        # Company description
        with st.expander("Business Description"):
            st.write(info.get('longBusinessSummary', 'No description available.'))
    
    def render_key_metrics(self, analysis):
        st.header("Key Metrics")
        
        metrics = analysis['profitability']
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "ROE",
                f"{metrics.get('roe', 0)*100:.2f}%"
            )
        
        with col2:
            st.metric(
                "ROA",
                f"{metrics.get('roa', 0)*100:.2f}%"
            )
        
        with col3:
            st.metric(
                "Net Margin",
                f"{metrics.get('net_margin', 0)*100:.2f}%"
            )
        
        with col4:
            st.metric(
                "Operating Margin",
                f"{metrics.get('operating_margin', 0)*100:.2f}%"
            )
    
    def render_financial_statements(self, financials):
        st.header("Financial Statements")
        
        tabs = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])
        
        with tabs[0]:
            if st.session_state.show_income:
                self.render_income_statement(financials['income_statement'])
        
        with tabs[1]:
            if st.session_state.show_balance:
                self.render_balance_sheet(financials['balance_sheet'])
        
        with tabs[2]:
            if st.session_state.show_cashflow:
                self.render_cash_flow(financials['cash_flow'])
    
    def render_ratio_analysis(self, analysis):
        st.header("Ratio Analysis")
        
        tabs = st.tabs(["Profitability", "Liquidity", "Solvency", "Efficiency"])
        
        with tabs[0]:
            if st.session_state.show_profitability:
                self.render_profitability_ratios(analysis['profitability'])
        
        with tabs[1]:
            if st.session_state.show_liquidity:
                self.render_liquidity_ratios(analysis['liquidity'])
        
        with tabs[2]:
            if st.session_state.show_solvency:
                self.render_solvency_ratios(analysis['solvency'])
        
        with tabs[3]:
            if st.session_state.show_efficiency:
                self.render_efficiency_ratios(analysis['efficiency'])
    
    def render_growth_analysis(self, analysis):
        st.header("Growth Analysis")
        
        growth = analysis['growth']
        
        # Create growth chart
        fig = go.Figure()
        
        metrics = ['revenue_growth', 'net_income_growth', 'eps_growth']
        for metric in metrics:
            fig.add_trace(
                go.Bar(
                    name=metric.replace('_', ' ').title(),
                    x=['YoY Growth'],
                    y=[growth.get(metric, 0)*100]
                )
            )
        
        fig.update_layout(
            title="Year-over-Year Growth Rates",
            yaxis_title="Growth Rate (%)",
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_valuation_analysis(self, analysis):
        st.header("Valuation Analysis")
        
        valuation = analysis['valuation']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Valuation metrics
            metrics = {
                'P/E Ratio': valuation.get('pe_ratio', 0),
                'P/B Ratio': valuation.get('price_to_book', 0),
                'EV/EBITDA': valuation.get('ev_to_ebitda', 0)
            }
            
            for name, value in metrics.items():
                st.metric(name, f"{value:.2f}")
        
        with col2:
            # Valuation comparison chart
            if 'Industry Average' in st.session_state.comparisons:
                self.render_valuation_comparison(valuation)
    
    def render_income_statement(self, data):
        """Render income statement with visualization."""
        # Format data
        df = pd.DataFrame(data)
        df = df.round(2)
        
        # Show table
        st.dataframe(df)
        
        # Create visualization
        fig = go.Figure()
        
        # Revenue and Net Income trends
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['Total Revenue'],
                name='Revenue'
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['Net Income'],
                name='Net Income'
            )
        )
        
        fig.update_layout(
            title="Revenue and Net Income Trends",
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_profitability_ratios(self, ratios):
        """Render profitability ratios with comparison."""
        fig = go.Figure()
        
        metrics = {
            'Gross Margin': ratios.get('gross_margin', 0),
            'Operating Margin': ratios.get('operating_margin', 0),
            'Net Margin': ratios.get('net_margin', 0),
            'ROE': ratios.get('roe', 0),
            'ROA': ratios.get('roa', 0)
        }
        
        fig.add_trace(
            go.Bar(
                x=list(metrics.keys()),
                y=[v*100 for v in metrics.values()],
                name='Company'
            )
        )
        
        if 'Industry Average' in st.session_state.comparisons:
            # Add industry average comparison
            pass
        
        fig.update_layout(
            title="Profitability Ratios",
            yaxis_title="Percentage (%)",
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    fundamental_page = FundamentalPage()
    fundamental_page.run()