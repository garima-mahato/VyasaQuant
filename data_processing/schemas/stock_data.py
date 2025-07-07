"""
Stock Data Schemas

Data structures for stock and financial market data.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import pandas as pd


@dataclass
class StockInfo:
    """Basic stock information"""
    symbol: str
    name: str
    exchange: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    currency: str = "INR"
    country: str = "India"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "name": self.name,
            "exchange": self.exchange,
            "sector": self.sector,
            "industry": self.industry,
            "market_cap": self.market_cap,
            "currency": self.currency,
            "country": self.country
        }


@dataclass
class StockPrice:
    """Stock price data point"""
    symbol: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "date": self.date.isoformat(),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "adjusted_close": self.adjusted_close
        }


@dataclass
class StockDataset:
    """Collection of stock data"""
    stock_info: StockInfo
    price_data: List[StockPrice] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert price data to pandas DataFrame"""
        if not self.price_data:
            return pd.DataFrame()
        
        data = [price.to_dict() for price in self.price_data]
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        return df.set_index('date')
    
    @property
    def date_range(self) -> tuple:
        """Get date range of the data"""
        if not self.price_data:
            return None, None
        
        dates = [price.date for price in self.price_data]
        return min(dates), max(dates)
    
    def get_latest_price(self) -> Optional[StockPrice]:
        """Get the most recent price data"""
        if not self.price_data:
            return None
        
        return max(self.price_data, key=lambda x: x.date) 