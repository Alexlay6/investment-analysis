import pandas as pd
import numpy as np
from typing import Dict, Any, List
import streamlit as st
from src.data.financial_data import FinancialDataLoader

class FundamentalAnalyzer:
    def __init__(self):
        self.financial_loader = FinancialDataLoader()
        
    @st.cache_data(ttl=86400)  # Cache for 1 day
    def analyze_company(self, ticker: str) -> Dict[str, Any]:
        """Perform comprehensive fundamental analysis."""
        try:
            # Get financial data
            financials = self.financial_loader.get_financial_statements(ticker)
            
            analysis = {
                'profitability': self._analyze_profitability(financials),
                'efficiency': self._analyze_efficiency(financials),
                'liquidity': self._analyze_liquidity(financials),
                'solvency': self._analyze_solvency(financials),
                'growth': self._analyze_growth(financials),
                'valuation': self._analyze_valuation(financials),
                'dupont': self._dupont_analysis(financials),
                'cash_flows': self._analyze_cash_flows(financials)
            }
            
            return analysis
        except Exception as e:
            st.error(f"Error in fundamental analysis: {str(e)}")
            return {}

    def _analyze_profitability(self, financials: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Analyze profitability metrics."""
        try:
            income_stmt = financials['income_statement']
            
            return {
                'gross_margin': self._calculate_ratio(
                    income_stmt['Gross Profit'],
                    income_stmt['Total Revenue']
                ),
                'operating_margin': self._calculate_ratio(
                    income_stmt['Operating Income'],
                    income_stmt['Total Revenue']
                ),
                'net_margin': self._calculate_ratio(
                    income_stmt['Net Income'],
                    income_stmt['Total Revenue']
                ),
                'roa': self._calculate_return_on_assets(financials),
                'roe': self._calculate_return_on_equity(financials)
            }
        except Exception as e:
            st.error(f"Error analyzing profitability: {str(e)}")
            return {}

    def _analyze_efficiency(self, financials: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Analyze operational efficiency metrics."""
        try:
            balance = financials['balance_sheet']
            income = financials['income_statement']
            
            return {
                'asset_turnover': self._calculate_ratio(
                    income['Total Revenue'],
                    balance['Total Assets'].mean()
                ),
                'inventory_turnover': self._calculate_inventory_turnover(financials),
                'receivables_turnover': self._calculate_receivables_turnover(financials),
                'payables_turnover': self._calculate_payables_turnover(financials),
                'cash_conversion_cycle': self._calculate_cash_conversion_cycle(financials)
            }
        except Exception as e:
            st.error(f"Error analyzing efficiency: {str(e)}")
            return {}

    def _analyze_liquidity(self, financials: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Analyze liquidity metrics."""
        try:
            balance = financials['balance_sheet']
            
            return {
                'current_ratio': self._calculate_ratio(
                    balance['Current Assets'],
                    balance['Current Liabilities']
                ),
                'quick_ratio': self._calculate_quick_ratio(balance),
                'cash_ratio': self._calculate_ratio(
                    balance['Cash and Cash Equivalents'],
                    balance['Current Liabilities']
                ),
                'working_capital': (
                    balance['Current Assets'] - balance['Current Liabilities']
                ).iloc[0]
            }
        except Exception as e:
            st.error(f"Error analyzing liquidity: {str(e)}")
            return {}

    def _analyze_solvency(self, financials: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Analyze solvency and leverage metrics."""
        try:
            balance = financials['balance_sheet']
            income = financials['income_statement']
            
            return {
                'debt_to_equity': self._calculate_ratio(
                    balance['Total Liabilities'],
                    balance['Total Stockholder Equity']
                ),
                'debt_to_assets': self._calculate_ratio(
                    balance['Total Liabilities'],
                    balance['Total Assets']
                ),
                'interest_coverage': self._calculate_ratio(
                    income['Operating Income'],
                    income['Interest Expense']
                ),
                'equity_multiplier': self._calculate_ratio(
                    balance['Total Assets'],
                    balance['Total Stockholder Equity']
                )
            }
        except Exception as e:
            st.error(f"Error analyzing solvency: {str(e)}")
            return {}

    def _analyze_growth(self, financials: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Analyze growth rates."""
        try:
            income = financials['income_statement']
            balance = financials['balance_sheet']
            
            return {
                'revenue_growth': self._calculate_growth_rate(income['Total Revenue']),
                'net_income_growth': self._calculate_growth_rate(income['Net Income']),
                'eps_growth': self._calculate_growth_rate(income['EPS']),
                'asset_growth': self._calculate_growth_rate(balance['Total Assets']),
                'equity_growth': self._calculate_growth_rate(balance['Total Stockholder Equity'])
            }
        except Exception as e:
            st.error(f"Error analyzing growth: {str(e)}")
            return {}

    def _analyze_valuation(self, financials: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Calculate valuation metrics."""
        try:
            info = financials['info']
            income = financials['income_statement']
            balance = financials['balance_sheet']
            
            market_cap = info.get('marketCap', 0)
            enterprise_value = self._calculate_enterprise_value(market_cap, balance)
            
            return {
                'pe_ratio': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'price_to_book': self._calculate_ratio(
                    market_cap,
                    balance['Total Stockholder Equity'].iloc[0]
                ),
                'ev_to_ebitda': self._calculate_ratio(
                    enterprise_value,
                    income['EBITDA'].iloc[0]
                ),
                'peg_ratio': info.get('pegRatio', 0),
                'dividend_yield': info.get('dividendYield', 0) * 100
            }
        except Exception as e:
            st.error(f"Error analyzing valuation: {str(e)}")
            return {}

    def _analyze_cash_flows(self, financials: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Analyze cash flow metrics."""
        try:
            cash_flow = financials['cash_flow']
            income = financials['income_statement']
            
            return {
                'operating_cash_flow_ratio': self._calculate_ratio(
                    cash_flow['Operating Cash Flow'],
                    income['Net Income']
                ),
                'free_cash_flow': self._calculate_fcf(cash_flow),
                'fcf_yield': self._calculate_fcf_yield(cash_flow, financials['info']),
                'capex_to_revenue': self._calculate_ratio(
                    cash_flow['Capital Expenditures'],
                    income['Total Revenue']
                )
            }
        except Exception as e:
            st.error(f"Error analyzing cash flows: {str(e)}")
            return {}

    def _dupont_analysis(self, financials: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Perform DuPont analysis."""
        try:
            income = financials['income_statement']
            balance = financials['balance_sheet']
            
            net_margin = self._calculate_ratio(
                income['Net Income'],
                income['Total Revenue']
            )
            
            asset_turnover = self._calculate_ratio(
                income['Total Revenue'],
                balance['Total Assets'].mean()
            )
            
            leverage = self._calculate_ratio(
                balance['Total Assets'],
                balance['Total Stockholder Equity']
            )
            
            return {
                'net_margin': net_margin,
                'asset_turnover': asset_turnover,
                'leverage': leverage,
                'roe_decomposition': {
                    'net_margin': net_margin,
                    'asset_turnover': asset_turnover,
                    'leverage': leverage,
                    'roe': net_margin * asset_turnover * leverage
                }
            }
        except Exception as e:
            st.error(f"Error in DuPont analysis: {str(e)}")
            return {}

    # Helper methods
    def _calculate_ratio(self, numerator: pd.Series, denominator: pd.Series) -> float:
        """Calculate financial ratio safely."""
        try:
            if denominator.iloc[0] != 0:
                return numerator.iloc[0] / denominator.iloc[0]
            return 0
        except:
            return 0

    def _calculate_growth_rate(self, series: pd.Series) -> float:
        """Calculate year-over-year growth rate."""
        try:
            if len(series) >= 2:
                return ((series.iloc[0] / series.iloc[1]) - 1) * 100
            return 0
        except:
            return 0

    def _calculate_quick_ratio(self, balance: pd.DataFrame) -> float:
        """Calculate quick ratio (acid-test ratio)."""
        try:
            quick_assets = (
                balance['Current Assets'].iloc[0] -
                balance['Inventory'].iloc[0]
            )
            return quick_assets / balance['Current Liabilities'].iloc[0]
        except:
            return 0

    def _calculate_enterprise_value(self, market_cap: float, balance: pd.DataFrame) -> float:
        """Calculate enterprise value."""
        try:
            return (
                market_cap +
                balance['Total Debt'].iloc[0] -
                balance['Cash and Cash Equivalents'].iloc[0]
            )
        except:
            return 0

    def _calculate_fcf(self, cash_flow: pd.DataFrame) -> float:
        """Calculate Free Cash Flow."""
        try:
            return (
                cash_flow['Operating Cash Flow'].iloc[0] -
                cash_flow['Capital Expenditures'].iloc[0]
            )
        except:
            return 0

    def _calculate_fcf_yield(self, cash_flow: pd.DataFrame, info: Dict[str, Any]) -> float:
        """Calculate Free Cash Flow Yield."""
        try:
            fcf = self._calculate_fcf(cash_flow)
            market_cap = info.get('marketCap', 0)
            if market_cap > 0:
                return (fcf / market_cap) * 100
            return 0
        except:
            return 0

    def generate_analysis_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a comprehensive analysis report."""
        try:
            report = f"""
            Fundamental Analysis Report
            
            1. Profitability Metrics:
            - Gross Margin: {analysis['profitability']['gross_margin']:.2%}
            - Operating Margin: {analysis['profitability']['operating_margin']:.2%}
            - Net Margin: {analysis['profitability']['net_margin']:.2%}
            - ROE: {analysis['profitability']['roe']:.2%}
            - ROA: {analysis['profitability']['roa']:.2%}
            
            2. Growth Analysis:
            - Revenue Growth: {analysis['growth']['revenue_growth']:.2f}%
            - Net Income Growth: {analysis['growth']['net_income_growth']:.2f}%
            - EPS Growth: {analysis['growth']['eps_growth']:.2f}%
            
            3. Valuation Metrics:
            - P/E Ratio: {analysis['valuation']['pe_ratio']:.2f}
            - Forward P/E: {analysis['valuation']['forward_pe']:.2f}
            - P/B Ratio: {analysis['valuation']['price_to_book']:.2f}
            - EV/EBITDA: {analysis['valuation']['ev_to_ebitda']:.2f}
            
            4. Financial Health:
            - Current Ratio: {analysis['liquidity']['current_ratio']:.2f}
            - Debt to Equity: {analysis['solvency']['debt_to_equity']:.2f}
            - Interest Coverage: {analysis['solvency']['interest_coverage']:.2f}
            
            5. Cash Flow Analysis:
            - FCF Yield: {analysis['cash_flows']['fcf_yield']:.2f}%
            - Operating Cash Flow Ratio: {analysis['cash_flows']['operating_cash_flow_ratio']:.2f}
            """
            
            return report
        except Exception as e:
            st.error(f"Error generating analysis report: {str(e)}")
            return "Error generating analysis report."