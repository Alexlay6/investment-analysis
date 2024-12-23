from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import streamlit as st

Base = declarative_base()

class StockData(Base):
    """Stock price and volume data."""
    __tablename__ = 'stock_data'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, index=True)
    timestamp = Column(DateTime, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'ticker': self.ticker,
            'timestamp': self.timestamp,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume
        }

class FinancialStatement(Base):
    """Financial statement data."""
    __tablename__ = 'financial_statements'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, index=True)
    statement_type = Column(String)  # income_statement, balance_sheet, cash_flow
    period_end = Column(DateTime, index=True)
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class Analysis(Base):
    """Analysis results."""
    __tablename__ = 'analysis'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, index=True)
    analysis_type = Column(String)  # technical, fundamental, risk, sentiment
    timestamp = Column(DateTime, index=True)
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class NewsArticle(Base):
    """News article data."""
    __tablename__ = 'news_articles'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, index=True)
    title = Column(String)
    content = Column(String)
    source = Column(String)
    url = Column(String)
    published_at = Column(DateTime, index=True)
    sentiment_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    """Manager class for database operations."""
    
    def __init__(self):
        self.engine = create_engine(st.secrets["DATABASE_URL"])
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_stock_data(self, data: Dict[str, Any]):
        """Save stock data to database."""
        session = self.Session()
        try:
            stock_data = StockData(**data)
            session.add(stock_data)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def save_financial_statement(self, data: Dict[str, Any]):
        """Save financial statement to database."""
        session = self.Session()
        try:
            statement = FinancialStatement(**data)
            session.add(statement)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def save_analysis(self, data: Dict[str, Any]):
        """Save analysis results to database."""
        session = self.Session()
        try:
            analysis = Analysis(**data)
            session.add(analysis)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def save_news_article(self, data: Dict[str, Any]):
        """Save news article to database."""
        session = self.Session()
        try:
            article = NewsArticle(**data)
            session.add(article)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_latest_stock_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get latest stock data for ticker."""
        session = self.Session()
        try:
            data = session.query(StockData)\
                .filter(StockData.ticker == ticker)\
                .order_by(StockData.timestamp.desc())\
                .first()
            return data.to_dict() if data else None
        finally:
            session.close()

    def get_analysis_history(self, ticker: str, 
                           analysis_type: str) -> List[Dict[str, Any]]:
        """Get analysis history for ticker."""
        session = self.Session()
        try:
            analyses = session.query(Analysis)\
                .filter(Analysis.ticker == ticker,
                       Analysis.analysis_type == analysis_type)\
                .order_by(Analysis.timestamp.desc())\
                .all()
            return [{'timestamp': a.timestamp, 'data': a.data} for a in analyses]
        finally:
            session.close()