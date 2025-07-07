"""
NSE Data Source
Handles data fetching from National Stock Exchange (NSE) of India.
"""

import requests
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from nsepython import *

logger = logging.getLogger(__name__)


class NSEDataSource:
    """Data source for NSE India stock exchange"""
    
    def __init__(self):
        self.base_url = "https://www.nseindia.com/api"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        })
    
    def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """Get current stock quote from NSE"""
        try:
            data = nsefetch(f"{self.base_url}/quote-equity?symbol={symbol}")
            return data
        except Exception as e:
            logger.error(f"Error fetching NSE quote for {symbol}: {e}")
            return {}
    
    def get_historical_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get historical stock data from NSE"""
        try:
            # NSE python doesn't have direct historical data API
            # This would need to be implemented with web scraping or third-party APIs
            logger.warning("Historical data not implemented for NSE source")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error fetching NSE historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """Get company information from NSE"""
        try:
            data = nsefetch(f"{self.base_url}/quote-equity?symbol={symbol}")
            if data and 'info' in data:
                return data['info']
            return {}
        except Exception as e:
            logger.error(f"Error fetching NSE company info for {symbol}: {e}")
            return {}
    
    def get_annual_reports(self, symbol: str) -> List[Dict[str, Any]]:
        """Get annual reports download links from NSE"""
        try:
            data = nsefetch(f"{self.base_url}/annual-reports?index=equities&symbol={symbol}")
            if data and 'data' in data:
                return data['data']
            return []
        except Exception as e:
            logger.error(f"Error fetching NSE annual reports for {symbol}: {e}")
            return []
    
    def search_stocks(self, query: str) -> List[Dict[str, Any]]:
        """Search for stocks on NSE"""
        try:
            data = nsefetch(f"{self.base_url}/search/autocomplete?q={query}")
            if data and 'symbols' in data:
                return data['symbols']
            return []
        except Exception as e:
            logger.error(f"Error searching NSE stocks for {query}: {e}")
            return []
    
    def get_sector_data(self, symbol: str) -> Dict[str, Any]:
        """Get sector information for a stock"""
        try:
            quote_data = self.get_stock_quote(symbol)
            if quote_data and 'industryInfo' in quote_data:
                return quote_data['industryInfo']
            return {}
        except Exception as e:
            logger.error(f"Error fetching NSE sector data for {symbol}: {e}")
            return {} 