import pandas as pd
import numpy as np
from typing import Dict, Any
import streamlit as st
from scipy import stats
from scipy.stats import norm

class RiskAnalyzer:
    def __init__(self):
        self.confidence_level = 0.95
        self.time_horizon = 10
        
    @st.cache_data(ttl=3600)
    def calculate_risk_metrics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive risk metrics for a stock."""
        returns = data['Close'].pct_change().dropna()
        
        risk_metrics = {
            'volatility': self._calculate_volatility(returns),
            'value_at_risk': self._calculate_var(returns),
            'beta': self._calculate_beta(returns),
            'drawdown': self._calculate_drawdown(data['Close']),
            'tail_risk': self._calculate_tail_risk(returns),
            'correlation': self._calculate_correlation(returns)
        }
        
        return risk_metrics
    
    def _calculate_volatility(self, returns: pd.Series) -> Dict[str, float]:
        """Calculate various volatility measures."""
        try:
            daily_vol = returns.std()
            annual_vol = daily_vol * np.sqrt(252)
            
            # Calculate rolling volatility
            rolling_vol = returns.rolling(window=30).std() * np.sqrt(252)
            
            # Estimate forward volatility using EWMA
            ewma_vol = returns.ewm(span=30).std() * np.sqrt(252)
            
            return {
                'daily_volatility': daily_vol,
                'annual_volatility': annual_vol,
                'current_rolling_vol': rolling_vol.iloc[-1],
                'forward_vol_estimate': ewma_vol.iloc[-1]
            }
        except Exception as e:
            st.error(f"Error calculating volatility: {str(e)}")
            return {}

    def _calculate_var(self, returns: pd.Series) -> Dict[str, float]:
        """Calculate Value at Risk metrics."""
        try:
            # Historical VaR
            hist_var = np.percentile(returns, (1 - self.confidence_level) * 100)
            
            # Parametric VaR
            mean = returns.mean()
            std = returns.std()
            param_var = norm.ppf(1 - self.confidence_level, mean, std)
            
            # Conditional VaR (Expected Shortfall)
            cvar = returns[returns <= hist_var].mean()
            
            var_metrics = {
                'historical_var': hist_var,
                'parametric_var': param_var,
                'conditional_var': cvar,
                'var_confidence': self.confidence_level,
                'time_horizon': self.time_horizon
            }
            
            return var_metrics
        except Exception as e:
            st.error(f"Error calculating VaR: {str(e)}")
            return {}

    def _calculate_beta(self, returns: pd.Series) -> Dict[str, float]:
        """Calculate beta and related market sensitivity metrics."""
        try:
            # Get market returns (S&P 500)
            import yfinance as yf
            market = yf.download('^GSPC', start=returns.index[0], end=returns.index[-1])
            market_returns = market['Close'].pct_change().dropna()
            
            # Calculate beta
            covar = returns.cov(market_returns)
            market_var = market_returns.var()
            beta = covar / market_var
            
            # Calculate R-squared
            correlation = returns.corr(market_returns)
            r_squared = correlation ** 2
            
            return {
                'beta': beta,
                'r_squared': r_squared,
                'correlation_with_market': correlation
            }
        except Exception as e:
            st.error(f"Error calculating beta: {str(e)}")
            return {}

    def _calculate_drawdown(self, prices: pd.Series) -> Dict[str, float]:
        """Calculate drawdown metrics."""
        try:
            # Calculate running maximum
            running_max = prices.expanding().max()
            drawdown = (prices - running_max) / running_max
            
            return {
                'current_drawdown': drawdown.iloc[-1],
                'max_drawdown': drawdown.min(),
                'avg_drawdown': drawdown.mean(),
                'drawdown_duration': self._calculate_drawdown_duration(drawdown)
            }
        except Exception as e:
            st.error(f"Error calculating drawdown: {str(e)}")
            return {}

    def _calculate_tail_risk(self, returns: pd.Series) -> Dict[str, float]:
        """Calculate tail risk metrics."""
        try:
            return {
                'skewness': returns.skew(),
                'kurtosis': returns.kurtosis(),
                'jarque_bera': stats.jarque_bera(returns)[0],
                'tail_ratio': abs(returns.quantile(0.99)) / abs(returns.quantile(0.01))
            }
        except Exception as e:
            st.error(f"Error calculating tail risk: {str(e)}")
            return {}

    def _calculate_correlation(self, returns: pd.Series) -> Dict[str, float]:
        """Calculate correlation with various market factors."""
        try:
            # Get returns for different market factors
            factors = {
                'SPY': 'S&P 500',
                'QQQ': 'NASDAQ',
                'IWM': 'Russell 2000',
                'VIX': 'Volatility Index'
            }
            
            correlations = {}
            for symbol, name in factors.items():
                try:
                    factor_data = yf.download(symbol, start=returns.index[0], end=returns.index[-1])
                    factor_returns = factor_data['Close'].pct_change().dropna()
                    correlations[name] = returns.corr(factor_returns)
                except:
                    continue
            
            return correlations
        except Exception as e:
            st.error(f"Error calculating correlations: {str(e)}")
            return {}

    def _calculate_drawdown_duration(self, drawdown: pd.Series) -> int:
        """Calculate the current drawdown duration in days."""
        try:
            # Find the last peak
            last_peak = drawdown[drawdown == 0].index[-1]
            return (drawdown.index[-1] - last_peak).days
        except:
            return 0

    def generate_risk_report(self, risk_metrics: Dict[str, Any]) -> str:
        """Generate a narrative risk report."""
        try:
            vol = risk_metrics['volatility']
            var = risk_metrics['value_at_risk']
            beta = risk_metrics['beta']
            
            report = f"""
            Risk Analysis Report:
            
            1. Volatility Analysis:
            - Annual Volatility: {vol['annual_volatility']:.2%}
            - Current Rolling Volatility: {vol['current_rolling_vol']:.2%}
            - Forward Volatility Estimate: {vol['forward_vol_estimate']:.2%}
            
            2. Value at Risk (VaR):
            - Historical VaR ({self.confidence_level*100}%): {var['historical_var']:.2%}
            - Conditional VaR: {var['conditional_var']:.2%}
            
            3. Market Sensitivity:
            - Beta: {beta['beta']:.2f}
            - R-Squared: {beta['r_squared']:.2f}
            - Market Correlation: {beta['correlation_with_market']:.2f}
            
            4. Drawdown Analysis:
            - Maximum Drawdown: {risk_metrics['drawdown']['max_drawdown']:.2%}
            - Current Drawdown: {risk_metrics['drawdown']['current_drawdown']:.2%}
            - Drawdown Duration: {risk_metrics['drawdown']['drawdown_duration']} days
            """
            
            return report
        except Exception as e:
            st.error(f"Error generating risk report: {str(e)}")
            return "Error generating risk report."