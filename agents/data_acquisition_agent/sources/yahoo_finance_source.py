"""
Yahoo Finance Data Source
Handles data fetching from Yahoo Finance API.
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class YahooFinanceDataSource:
    """Data source for Yahoo Finance"""
    
    def __init__(self):
        self.suffix = ".NS"  # NSE suffix for Indian stocks
    
    def _get_ticker_symbol(self, symbol: str) -> str:
        """Convert NSE symbol to Yahoo Finance symbol"""
        if not symbol.endswith(self.suffix):
            return f"{symbol}{self.suffix}"
        return symbol
    
    def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """Get current stock quote from Yahoo Finance"""
        try:
            ticker_symbol = self._get_ticker_symbol(symbol)
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'currentPrice': info.get('currentPrice'),
                'dayHigh': info.get('dayHigh'),
                'dayLow': info.get('dayLow'),
                'volume': info.get('volume'),
                'marketCap': info.get('marketCap'),
                'pe_ratio': info.get('forwardPE'),
                'dividend_yield': info.get('dividendYield'),
                'beta': info.get('beta'),
                'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh'),
                'fiftyTwoWeekLow': info.get('fiftyTwoWeekLow')
            }
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance quote for {symbol}: {e}")
            return {}
    
    def get_historical_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Get historical stock data from Yahoo Finance"""
        try:
            ticker_symbol = self._get_ticker_symbol(symbol)
            ticker = yf.Ticker(ticker_symbol)
            data = ticker.history(period=period)
            
            # Reset index to make Date a column
            data = data.reset_index()
            data['Symbol'] = symbol
            
            return data
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_financial_statements(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """Get financial statements from Yahoo Finance"""
        try:
            ticker_symbol = self._get_ticker_symbol(symbol)
            ticker = yf.Ticker(ticker_symbol)
            
            statements = {}
            
            # Get balance sheet
            try:
                statements['balance_sheet'] = ticker.balance_sheet
            except:
                statements['balance_sheet'] = pd.DataFrame()
            
            # Get income statement
            try:
                statements['income_statement'] = ticker.financials
            except:
                statements['income_statement'] = pd.DataFrame()
            
            # Get cash flow statement
            try:
                statements['cash_flow'] = ticker.cashflow
            except:
                statements['cash_flow'] = pd.DataFrame()
            
            return statements
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance financial statements for {symbol}: {e}")
            return {}
    
    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """Get company information from Yahoo Finance"""
        try:
            ticker_symbol = self._get_ticker_symbol(symbol)
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'longName': info.get('longName'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'country': info.get('country'),
                'website': info.get('website'),
                'business_summary': info.get('longBusinessSummary'),
                'employees': info.get('fullTimeEmployees'),
                'market_cap': info.get('marketCap'),
                'enterprise_value': info.get('enterpriseValue'),
                'trailing_pe': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'price_to_book': info.get('priceToBook'),
                'debt_to_equity': info.get('debtToEquity'),
                'return_on_equity': info.get('returnOnEquity'),
                'return_on_assets': info.get('returnOnAssets')
            }
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance company info for {symbol}: {e}")
            return {}
    
    def get_dividends(self, symbol: str, period: str = "5y") -> pd.DataFrame:
        """Get dividend history from Yahoo Finance"""
        try:
            ticker_symbol = self._get_ticker_symbol(symbol)
            ticker = yf.Ticker(ticker_symbol)
            dividends = ticker.dividends
            
            # Convert to DataFrame
            if not dividends.empty:
                df = dividends.to_frame('Dividend')
                df = df.reset_index()
                df['Symbol'] = symbol
                return df
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance dividends for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_options_data(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """Get options data from Yahoo Finance"""
        try:
            ticker_symbol = self._get_ticker_symbol(symbol)
            ticker = yf.Ticker(ticker_symbol)
            
            options_data = {}
            
            # Get options expiration dates
            exp_dates = ticker.options
            
            if exp_dates:
                # Get data for the nearest expiration
                nearest_exp = exp_dates[0]
                option_chain = ticker.option_chain(nearest_exp)
                
                options_data['calls'] = option_chain.calls
                options_data['puts'] = option_chain.puts
                options_data['expiration_date'] = nearest_exp
            
            return options_data
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance options data for {symbol}: {e}")
            return {} 