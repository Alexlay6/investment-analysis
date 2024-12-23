import pandas as pd
from typing import Dict, Any, List
import streamlit as st
from datetime import datetime, timedelta
import numpy as np
from anthropic import Anthropic
from textblob import TextBlob
import re

class SentimentAnalyzer:
    def __init__(self):
        self.anthropic = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
        self.sentiment_weights = {
            'news': 0.4,
            'social_media': 0.3,
            'financial_reports': 0.3
        }

    @st.cache_data(ttl=3600)
    def analyze_sentiment(self, ticker: str, news_data: List[Dict], 
                         financial_reports: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive sentiment analysis."""
        try:
            # Analyze different sources
            news_sentiment = self._analyze_news_sentiment(news_data)
            social_sentiment = self._analyze_social_media_sentiment(ticker)
            report_sentiment = self._analyze_financial_reports_sentiment(financial_reports)
            
            # Combine sentiments
            combined_sentiment = self._combine_sentiment_scores(
                news_sentiment,
                social_sentiment,
                report_sentiment
            )
            
            return {
                'overall_sentiment': combined_sentiment,
                'news_sentiment': news_sentiment,
                'social_sentiment': social_sentiment,
                'report_sentiment': report_sentiment,
                'sentiment_trends': self._analyze_sentiment_trends(news_data),
                'key_topics': self._extract_key_topics(news_data)
            }
        except Exception as e:
            st.error(f"Error in sentiment analysis: {str(e)}")
            return {}

    def _analyze_news_sentiment(self, news_data: List[Dict]) -> Dict[str, Any]:
        """Analyze sentiment from news articles."""
        try:
            sentiments = []
            for article in news_data:
                # Combine title and content for analysis
                text = f"{article['title']} {article.get('description', '')}"
                
                # Get sentiment scores
                blob_sentiment = TextBlob(text).sentiment
                
                sentiments.append({
                    'date': article['published_at'],
                    'score': blob_sentiment.polarity,
                    'subjectivity': blob_sentiment.subjectivity,
                    'source': article['source'],
                    'title': article['title']
                })
            
            # Calculate aggregate metrics
            sentiment_df = pd.DataFrame(sentiments)
            
            return {
                'average_score': sentiment_df['score'].mean(),
                'sentiment_distribution': {
                    'positive': len(sentiment_df[sentiment_df['score'] > 0.2]),
                    'neutral': len(sentiment_df[(sentiment_df['score'] >= -0.2) & 
                                             (sentiment_df['score'] <= 0.2)]),
                    'negative': len(sentiment_df[sentiment_df['score'] < -0.2])
                },
                'source_analysis': self._analyze_sentiment_by_source(sentiment_df),
                'recent_sentiments': sentiments[:5]  # Most recent articles
            }
        except Exception as e:
            st.error(f"Error analyzing news sentiment: {str(e)}")
            return {}

    def _analyze_social_media_sentiment(self, ticker: str) -> Dict[str, Any]:
        """Analyze sentiment from social media sources."""
        try:
            # Placeholder for social media API integrations
            # Would typically include Twitter, Reddit, StockTwits, etc.
            
            return {
                'average_score': 0.0,
                'platform_scores': {
                    'twitter': 0.0,
                    'reddit': 0.0,
                    'stocktwits': 0.0
                },
                'mention_volume': {
                    'total': 0,
                    'positive': 0,
                    'negative': 0
                }
            }
        except Exception as e:
            st.error(f"Error analyzing social media sentiment: {str(e)}")
            return {}

    def _analyze_financial_reports_sentiment(self, reports: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment from financial reports using Claude."""
        try:
            if not reports:
                return {}
                
            # Prepare text for analysis
            report_text = self._prepare_report_text(reports)
            
            # Analyze with Claude
            prompt = f"""
            Please analyze the sentiment and tone of these financial report excerpts.
            Focus on:
            1. Management's confidence and outlook
            2. Risk factors and concerns
            3. Forward-looking statements
            4. Key strategic initiatives
            
            Text:
            {report_text}
            
            Provide a structured analysis with sentiment scores and key points.
            """
            
            response = self.anthropic.messages.create(
                model="claude-3-opus-20240229",
                temperature=0,
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Process Claude's response
            analysis = self._parse_claude_response(response.content)
            
            return analysis
        except Exception as e:
            st.error(f"Error analyzing financial reports sentiment: {str(e)}")
            return {}

    def _combine_sentiment_scores(self, news: Dict[str, Any], 
                                social: Dict[str, Any], 
                                reports: Dict[str, Any]) -> float:
        """Combine sentiment scores from different sources."""
        try:
            scores = {
                'news': news.get('average_score', 0) * self.sentiment_weights['news'],
                'social': social.get('average_score', 0) * self.sentiment_weights['social_media'],
                'reports': reports.get('sentiment_score', 0) * self.sentiment_weights['financial_reports']
            }
            
            return sum(scores.values())
        except Exception as e:
            st.error(f"Error combining sentiment scores: {str(e)}")
            return 0.0

    def _analyze_sentiment_trends(self, news_data: List[Dict]) -> Dict[str, Any]:
        """Analyze sentiment trends over time."""
        try:
            # Convert news data to DataFrame
            df = pd.DataFrame(news_data)
            df['date'] = pd.to_datetime(df['published_at'])
            df.set_index('date', inplace=True)
            
            # Calculate daily sentiment averages
            daily_sentiment = df.resample('D')['sentiment_score'].mean()
            
            return {
                'trend': self._calculate_trend(daily_sentiment),
                'volatility': daily_sentiment.std(),
                'momentum': self._calculate_sentiment_momentum(daily_sentiment)
            }
        except Exception as e:
            st.error(f"Error analyzing sentiment trends: {str(e)}")
            return {}

    def _extract_key_topics(self, news_data: List[Dict]) -> List[Dict[str, Any]]:
        """Extract and analyze key topics from news."""
        try:
            # Combine all text
            all_text = ' '.join([
                f"{article['title']} {article.get('description', '')}"
                for article in news_data
            ])
            
            # Use Claude to extract topics
            prompt = f"""
            Please identify the main topics and themes in these news articles.
            Focus on:
            1. Key business events
            2. Market factors
            3. Industry trends
            4. Company-specific news
            
            Text:
            {all_text}
            
            List the top themes with their frequency and significance.
            """
            
            response = self.anthropic.messages.create(
                model="claude-3-opus-20240229",
                temperature=0,
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Process and structure topics
            topics = self._process_topics(response.content)
            
            return topics
        except Exception as e:
            st.error(f"Error extracting key topics: {str(e)}")
            return []

    def _analyze_sentiment_by_source(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze sentiment patterns by news source."""
        try:
            source_analysis = df.groupby('source').agg({
                'score': ['mean', 'std', 'count'],
                'subjectivity': 'mean'
            }).round(3)
            
            return source_analysis.to_dict()
        except Exception as e:
            st.error(f"Error analyzing sentiment by source: {str(e)}")
            return {}

    def _calculate_trend(self, series: pd.Series) -> str:
        """Calculate the trend direction of sentiment."""
        try:
            if len(series) < 2:
                return "neutral"
                
            slope = np.polyfit(range(len(series)), series.values, 1)[0]
            
            if slope > 0.01:
                return "improving"
            elif slope < -0.01:
                return "deteriorating"
            return "stable"
        except Exception as e:
            st.error(f"Error calculating trend: {str(e)}")
            return "neutral"

    def _calculate_sentiment_momentum(self, series: pd.Series) -> float:
        """Calculate sentiment momentum (rate of change)."""
        try:
            if len(series) < 5:
                return 0.0
                
            recent_avg = series[-5:].mean()
            older_avg = series[-10:-5].mean()
            
            return ((recent_avg - older_avg) / older_avg) * 100
        except Exception as e:
            st.error(f"Error calculating sentiment momentum: {str(e)}")
            return 0.0

    def _parse_claude_response(self, response: str) -> Dict[str, Any]:
        """Parse and structure Claude's analysis response."""
        try:
            # Extract sentiment score (assuming Claude provides a normalized score)
            score_match = re.search(r'sentiment score[:\s]+(-?\d+\.?\d*)', 
                                  response.lower())
            sentiment_score = float(score_match.group(1)) if score_match else 0.0
            
            # Extract key points
            key_points = re.findall(r'•\s+([^•\n]+)', response)
            
            return {
                'sentiment_score': sentiment_score,
                'key_points': key_points,
                'full_analysis': response
            }
        except Exception as e:
            st.error(f"Error parsing Claude response: {str(e)}")
            return {}