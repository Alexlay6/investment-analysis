from .technical import TechnicalAnalyzer
from .fundamental import FundamentalAnalyzer
from .risk import RiskAnalyzer
from .sentiment import SentimentAnalyzer
from typing import Dict, List, Any
import pandas as pd
import streamlit as st

class AnalysisManager:
    """Manager class to coordinate different types of analysis."""
    
    def __init__(self):
        self.technical = TechnicalAnalyzer()
        self.fundamental = FundamentalAnalyzer()
        self.risk = RiskAnalyzer()
        self.sentiment = SentimentAnalyzer()
    
    def perform_complete_analysis(self, ticker: str, 
                                market_data: pd.DataFrame,
                                news_data: List[Dict],
                                financial_reports: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive analysis using all analyzers."""
        try:
            # Technical Analysis
            technical_analysis = self.technical.analyze_price_action(market_data)
            
            # Fundamental Analysis
            fundamental_analysis = self.fundamental.analyze_company(ticker)
            
            # Risk Analysis
            risk_analysis = self.risk.calculate_risk_metrics(market_data)
            
            # Sentiment Analysis
            sentiment_analysis = self.sentiment.analyze_sentiment(
                ticker, 
                news_data, 
                financial_reports
            )
            
            return {
                'technical': technical_analysis,
                'fundamental': fundamental_analysis,
                'risk': risk_analysis,
                'sentiment': sentiment_analysis,
                'summary': self._generate_summary(
                    technical_analysis,
                    fundamental_analysis,
                    risk_analysis,
                    sentiment_analysis
                )
            }
        except Exception as e:
            st.error(f"Error in complete analysis: {str(e)}")
            return {}
    
    def _generate_summary(self, technical: Dict[str, Any],
                         fundamental: Dict[str, Any],
                         risk: Dict[str, Any],
                         sentiment: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of all analyses."""
        try:
            return {
                'overall_rating': self._calculate_overall_rating(
                    technical, fundamental, risk, sentiment
                ),
                'key_findings': self._extract_key_findings(
                    technical, fundamental, risk, sentiment
                ),
                'recommendations': self._generate_recommendations(
                    technical, fundamental, risk, sentiment
                )
            }
        except Exception as e:
            st.error(f"Error generating summary: {str(e)}")
            return {}
    
    def _calculate_overall_rating(self, *analyses) -> str:
        """Calculate overall investment rating."""
        try:
            # Implement rating logic based on all analyses
            scores = {
                'technical': self._score_technical(analyses[0]),
                'fundamental': self._score_fundamental(analyses[1]),
                'risk': self._score_risk(analyses[2]),
                'sentiment': self._score_sentiment(analyses[3])
            }
            
            total_score = sum(scores.values()) / len(scores)
            
            if total_score >= 8:
                return "Strong Buy"
            elif total_score >= 6:
                return "Buy"
            elif total_score >= 4:
                return "Hold"
            elif total_score >= 2:
                return "Sell"
            else:
                return "Strong Sell"
        except Exception as e:
            st.error(f"Error calculating overall rating: {str(e)}")
            return "N/A"
    
    def _score_technical(self, analysis: Dict[str, Any]) -> float:
        """Score technical analysis results."""
        score = 5.0  # Neutral starting point
        if not analysis:
            return score
            
        try:
            # Adjust score based on technical signals
            if analysis.get('trends', {}).get('overall', {}).get('direction') == 'bullish':
                score += 1
            elif analysis.get('trends', {}).get('overall', {}).get('direction') == 'bearish':
                score -= 1
                
            # Add momentum impact
            momentum = analysis.get('momentum', {}).get('macd', {})
            if momentum.get('trend') == 'bullish':
                score += 1
            elif momentum.get('trend') == 'bearish':
                score -= 1
                
            return min(max(score, 0), 10)  # Ensure score is between 0 and 10
        except:
            return score
            
    def _score_fundamental(self, analysis: Dict[str, Any]) -> float:
        """Score fundamental analysis results."""
        score = 5.0
        if not analysis:
            return score
            
        try:
            # Adjust score based on fundamental factors
            profitability = analysis.get('profitability', {})
            growth = analysis.get('growth', {})
            
            # Profitability impact
            # Profitability impact
            if profitability.get('net_margin', 0) > 0.15:
                score += 1
            elif profitability.get('net_margin', 0) < 0:
                score -= 1
                
            # Growth impact
            revenue_growth = growth.get('revenue_growth', 0)
            if revenue_growth > 20:
                score += 2
            elif revenue_growth > 10:
                score += 1
            elif revenue_growth < 0:
                score -= 1
                
            return min(max(score, 0), 10)
        except:
            return score
    
    def _score_risk(self, analysis: Dict[str, Any]) -> float:
        """Score risk analysis results."""
        score = 5.0
        if not analysis:
            return score
            
        try:
            # Adjust score based on risk metrics
            volatility = analysis.get('volatility', {})
            var = analysis.get('value_at_risk', {})
            
            # Volatility impact
            if volatility.get('annual_volatility', 0) > 0.4:
                score -= 2
            elif volatility.get('annual_volatility', 0) > 0.25:
                score -= 1
                
            # VaR impact
            if var.get('historical_var', 0) < -0.1:
                score -= 1
                
            # Beta impact
            beta = analysis.get('beta', {}).get('beta', 1)
            if beta > 1.5:
                score -= 1
            elif beta < 0.8:
                score += 1
                
            return min(max(score, 0), 10)
        except:
            return score
    
    def _score_sentiment(self, analysis: Dict[str, Any]) -> float:
        """Score sentiment analysis results."""
        score = 5.0
        if not analysis:
            return score
            
        try:
            # Overall sentiment impact
            sentiment_score = analysis.get('overall_sentiment', 0)
            if sentiment_score > 0.5:
                score += 2
            elif sentiment_score > 0.2:
                score += 1
            elif sentiment_score < -0.2:
                score -= 1
            elif sentiment_score < -0.5:
                score -= 2
                
            # News sentiment trend
            trend = analysis.get('sentiment_trends', {}).get('trend')
            if trend == 'improving':
                score += 1
            elif trend == 'deteriorating':
                score -= 1
                
            return min(max(score, 0), 10)
        except:
            return score
    
    def _extract_key_findings(self, technical: Dict[str, Any],
                            fundamental: Dict[str, Any],
                            risk: Dict[str, Any],
                            sentiment: Dict[str, Any]) -> List[str]:
        """Extract key findings from all analyses."""
        findings = []
        
        try:
            # Technical findings
            if technical.get('trends', {}).get('overall', {}).get('direction'):
                findings.append(f"Technical Trend: {technical['trends']['overall']['direction']}")
                
            # Fundamental findings
            if fundamental.get('growth', {}).get('revenue_growth'):
                findings.append(
                    f"Revenue Growth: {fundamental['growth']['revenue_growth']:.1f}%"
                )
                
            # Risk findings
            if risk.get('volatility', {}).get('annual_volatility'):
                findings.append(
                    f"Annual Volatility: {risk['volatility']['annual_volatility']:.1%}"
                )
                
            # Sentiment findings
            if sentiment.get('overall_sentiment'):
                findings.append(
                    f"Market Sentiment: {self._classify_sentiment(sentiment['overall_sentiment'])}"
                )
                
            return findings
        except Exception as e:
            st.error(f"Error extracting key findings: {str(e)}")
            return []
    
    def _generate_recommendations(self, technical: Dict[str, Any],
                                fundamental: Dict[str, Any],
                                risk: Dict[str, Any],
                                sentiment: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate actionable recommendations."""
        try:
            recommendations = {
                'action': [],
                'watch_points': [],
                'risk_management': []
            }
            
            # Technical-based recommendations
            tech_trend = technical.get('trends', {}).get('overall', {}).get('direction')
            if tech_trend == 'bullish':
                recommendations['action'].append("Consider entry points on pullbacks")
            elif tech_trend == 'bearish':
                recommendations['action'].append("Consider reducing position size")
            
            # Fundamental-based recommendations
            growth = fundamental.get('growth', {}).get('revenue_growth', 0)
            margins = fundamental.get('profitability', {}).get('net_margin', 0)
            if growth > 20 and margins > 0.15:
                recommendations['action'].append("Consider long-term position building")
            elif growth < 0 or margins < 0:
                recommendations['action'].append("Review fundamental factors before adding")
            
            # Risk-based recommendations
            volatility = risk.get('volatility', {}).get('annual_volatility', 0)
            if volatility > 0.3:
                recommendations['risk_management'].append(
                    f"Consider position sizing due to high volatility ({volatility:.1%})"
                )
            
            var = risk.get('value_at_risk', {}).get('historical_var', 0)
            recommendations['risk_management'].append(
                f"Set stop loss considering VaR: {var:.1%}"
            )
            
            # Sentiment-based recommendations
            sentiment_score = sentiment.get('overall_sentiment', 0)
            if sentiment_score > 0.5:
                recommendations['watch_points'].append("Monitor for potential profit taking")
            elif sentiment_score < -0.5:
                recommendations['watch_points'].append("Watch for sentiment reversal")
            
            return recommendations
        except Exception as e:
            st.error(f"Error generating recommendations: {str(e)}")
            return {'action': [], 'watch_points': [], 'risk_management': []}
    
    def _classify_sentiment(self, sentiment_score: float) -> str:
        """Classify sentiment score into categories."""
        if sentiment_score > 0.5:
            return "Very Positive"
        elif sentiment_score > 0.2:
            return "Positive"
        elif sentiment_score > -0.2:
            return "Neutral"
        elif sentiment_score > -0.5:
            return "Negative"
        else:
            return "Very Negative"

# Export all analyzers and manager
__all__ = [
    'TechnicalAnalyzer',
    'FundamentalAnalyzer',
    'RiskAnalyzer',
    'SentimentAnalyzer',
    'AnalysisManager'
]