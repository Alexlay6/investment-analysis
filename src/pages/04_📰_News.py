import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.data import NewsDataLoader
from src.analysis import SentimentAnalyzer
from src.utils import TimeHelper

# Page configuration
st.set_page_config(
    page_title="News & Sentiment",
    page_icon="📰",
    layout="wide"
)

class NewsPage:
    def __init__(self):
        self.news_loader = NewsDataLoader()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.time_helper = TimeHelper()
        
    def run(self):
        st.title("News & Sentiment Analysis")
        
        # Sidebar controls
        with st.sidebar:
            self.render_sidebar()
        
        # Get data
        ticker = st.session_state.get('ticker', 'AAPL')
        days = st.session_state.get('news_days', 30)
        
        try:
            # Get news and sentiment data
            news_data = self.news_loader.get_company_news(ticker, days)
            sentiment_analysis = self.sentiment_analyzer.analyze_sentiment(
                ticker, news_data, {}
            )
            
            # Render different sections
            self.render_sentiment_overview(sentiment_analysis)
            self.render_sentiment_trends(sentiment_analysis)
            self.render_news_feed(news_data)
            self.render_topic_analysis(sentiment_analysis)
            self.render_social_media_sentiment(sentiment_analysis)
            
        except Exception as e:
            st.error(f"Error loading news and sentiment data: {str(e)}")
    
    def render_sidebar(self):
        st.title("News Settings")
        
        # Time range
        st.subheader("Time Range")
        st.slider(
            "Days to analyze",
            min_value=7,
            max_value=90,
            value=30,
            step=1,
            key='news_days'
        )
        
        # News sources
        st.subheader("News Sources")
        st.multiselect(
            "Select Sources",
            options=['All', 'Financial News', 'Press Releases', 'SEC Filings'],
            default=['All'],
            key='news_sources'
        )
        
        # Sentiment filters
        st.subheader("Sentiment Filter")
        st.select_slider(
            "Sentiment Range",
            options=['Very Negative', 'Negative', 'Neutral', 'Positive', 'Very Positive'],
            value=('Very Negative', 'Very Positive'),
            key='sentiment_range'
        )
        
        # Topic filters
        st.subheader("Topic Filter")
        st.multiselect(
            "Select Topics",
            options=['Earnings', 'Products', 'Management', 'Markets', 'Competition'],
            key='topics'
        )
    
    def render_sentiment_overview(self, sentiment_analysis):
        st.header("Sentiment Overview")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            overall_score = sentiment_analysis['overall_sentiment']
            st.metric(
                "Overall Sentiment",
                f"{overall_score:.2f}",
                delta=self._get_sentiment_trend(sentiment_analysis)
            )
        
        with col2:
            sentiment_dist = sentiment_analysis['news_sentiment']['sentiment_distribution']
            total_articles = sum(sentiment_dist.values())
            positive_ratio = sentiment_dist['positive'] / total_articles
            st.metric(
                "Positive News Ratio",
                f"{positive_ratio:.1%}"
            )
        
        with col3:
            source_analysis = sentiment_analysis['news_sentiment']['source_analysis']
            avg_reliability = np.mean([s.get('reliability', 0) for s in source_analysis.values()])
            st.metric(
                "Source Reliability",
                f"{avg_reliability:.1%}"
            )
        
        # Sentiment gauge chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = (overall_score + 1) * 50,  # Convert -1 to 1 to 0 to 100
            gauge = {
                'axis': {'range': [0, 100]},
                'steps': [
                    {'range': [0, 33], 'color': "lightgray"},
                    {'range': [33, 66], 'color': "gray"},
                    {'range': [66, 100], 'color': "darkgray"}
                ],
                'bar': {'color': self._get_sentiment_color(overall_score)}
            }
        ))
        
        fig.update_layout(height=200)
        st.plotly_chart(fig, use_container_width=True)
    
    def render_sentiment_trends(self, sentiment_analysis):
        st.header("Sentiment Trends")
        
        # Get sentiment trends data
        trends = sentiment_analysis['sentiment_trends']
        
        # Create line chart
        fig = go.Figure()
        
        fig.add_trace(
            go.Scatter(
                x=trends['dates'],
                y=trends['sentiment_scores'],
                name='Daily Sentiment',
                line=dict(color='blue')
            )
        )
        
        # Add moving average
        fig.add_trace(
            go.Scatter(
                x=trends['dates'],
                y=pd.Series(trends['sentiment_scores']).rolling(7).mean(),
                name='7-Day Moving Average',
                line=dict(color='red', dash='dash')
            )
        )
        
        fig.update_layout(
            title="Sentiment Score Trends",
            xaxis_title="Date",
            yaxis_title="Sentiment Score",
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_news_feed(self, news_data):
        st.header("News Feed")
        
        # Filter news based on sentiment range
        sentiment_range = st.session_state.sentiment_range
        filtered_news = self._filter_news_by_sentiment(news_data, sentiment_range)
        
        # Create tabs for different news categories
        tabs = st.tabs(["All News", "High Impact", "Press Releases", "SEC Filings"])
        
        with tabs[0]:
            self._render_news_list(filtered_news)
        
        with tabs[1]:
            high_impact = [n for n in filtered_news if n.get('impact_score', 0) > 0.7]
            self._render_news_list(high_impact)
        
        with tabs[2]:
            press_releases = [n for n in filtered_news if n['source'] == 'Press Release']
            self._render_news_list(press_releases)
        
        with tabs[3]:
            sec_filings = [n for n in filtered_news if n['source'] == 'SEC']
            self._render_news_list(sec_filings)
    
    def render_topic_analysis(self, sentiment_analysis):
        st.header("Topic Analysis")
        
        topics = sentiment_analysis.get('key_topics', [])
        
        # Create treemap of topics
        fig = go.Figure(go.Treemap(
            labels=[topic['topic'] for topic in topics],
            parents=[''] * len(topics),
            values=[topic['frequency'] for topic in topics],
            textinfo="label+value+percent parent"
        ))
        
        fig.update_layout(
            title="News Topics Distribution",
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Topic sentiment analysis
        topic_sentiment = pd.DataFrame(topics)
        if not topic_sentiment.empty:
            st.subheader("Topic Sentiment Analysis")
            
            fig = go.Figure(go.Bar(
                x=topic_sentiment['topic'],
                y=topic_sentiment['sentiment'],
                marker_color=topic_sentiment['sentiment'].apply(self._get_sentiment_color)
            ))
            
            fig.update_layout(
                title="Sentiment by Topic",
                xaxis_title="Topic",
                yaxis_title="Sentiment Score",
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def render_social_media_sentiment(self, sentiment_analysis):
        st.header("Social Media Sentiment")
        
        social = sentiment_analysis.get('social_sentiment', {})
        
        # Create radar chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=[
                social.get('twitter_sentiment', 0),
                social.get('reddit_sentiment', 0),
                social.get('stocktwits_sentiment', 0),
                social.get('youtube_sentiment', 0)
            ],
            theta=['Twitter', 'Reddit', 'StockTwits', 'YouTube'],
            fill='toself'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[-1, 1]
                )
            ),
            title="Social Media Sentiment Analysis",
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Social media metrics
        with st.expander("Social Media Metrics"):
            col1, col2 = st.columns(2)
            
            with col1:
                metrics = social.get('metrics', {})
                st.metric("Mention Volume", metrics.get('mention_volume', 0))
                st.metric("Engagement Rate", f"{metrics.get('engagement_rate', 0):.2%}")
            
            with col2:
                st.metric("Positive Mentions", metrics.get('positive_mentions', 0))
                st.metric("Negative Mentions", metrics.get('negative_mentions', 0))
    
    def _render_news_list(self, news_list):
        """Render a list of news articles."""
        for article in news_list:
            with st.expander(article['title']):
                st.write(article['description'])
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.caption(f"Source: {article['source']}")
                
                with col2:
                    st.caption(f"Published: {article['published_at']}")
                
                with col3:
                    sentiment = article.get('sentiment', 0)
                    st.progress(
                        (sentiment + 1) / 2,
                        text=f"Sentiment: {sentiment:.2f}"
                    )
    
    def _get_sentiment_trend(self, analysis):
        """Calculate sentiment trend."""
        trend = analysis['sentiment_trends'].get('trend', 0)
        return f"{trend:+.2f}" if trend != 0 else None
    
    def _get_sentiment_color(self, sentiment):
        """Get color based on sentiment score."""
        if sentiment > 0.33:
            return 'green'
        elif sentiment < -0.33:
            return 'red'
        return 'gray'
    
    def _filter_news_by_sentiment(self, news_data, sentiment_range):
        """Filter news articles based on sentiment range."""
        sentiment_values = {
            'Very Negative': -1.0,
            'Negative': -0.33,
            'Neutral': 0,
            'Positive': 0.33,
            'Very Positive': 1.0
        }
        
        min_sentiment = sentiment_values[sentiment_range[0]]
        max_sentiment = sentiment_values[sentiment_range[1]]
        
        return [
            article for article in news_data
            if min_sentiment <= article.get('sentiment', 0) <= max_sentiment
        ]

if __name__ == "__main__":
    news_page = NewsPage()
    news_page.run()