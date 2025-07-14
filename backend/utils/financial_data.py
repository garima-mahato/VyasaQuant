import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class FinancialDataManager:
    """Manager for financial data operations using yfinance and external APIs"""
    
    def __init__(self):
        self.financial_year_start_month = 4  # April
    
    def get_current_financial_year(self) -> int:
        """Get current financial year based on April start"""
        current_date = datetime.now()
        if current_date.month >= self.financial_year_start_month:
            return current_date.year
        else:
            return current_date.year - 1
    
    def get_ticker_data(self, ticker: str) -> Optional[yf.Ticker]:
        """Get yfinance Ticker object"""
        try:
            return yf.Ticker(ticker)
        except Exception as e:
            logger.error(f"Error getting ticker data for {ticker}: {str(e)}")
            return None
    
    def get_basic_stock_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get basic stock information including company name and TTM EPS"""
        try:
            dat = self.get_ticker_data(ticker)
            if dat is None:
                return None
            
            info = dat.info
            stock_symbol = ticker.split('.NS')[0]
            
            # Extract relevant information
            stock_info = {
                'stock_symbol': stock_symbol,
                'Ticker': ticker,
                'Stock_Name': info.get('longName', info.get('shortName', '')),
                'Current_Financial_Year': str(self.get_current_financial_year()),
                'eps_ttm': info.get('epsTrailingTwelveMonths')
            }
            
            logger.info(f"Retrieved basic info for {ticker}: {stock_info['Stock_Name']}")
            return stock_info
            
        except Exception as e:
            logger.error(f"Error getting basic stock info for {ticker}: {str(e)}")
            return None
    
    def get_financial_statements(self, ticker: str) -> Optional[pd.DataFrame]:
        """Get financial statements data"""
        try:
            dat = self.get_ticker_data(ticker)
            if dat is None:
                return None
            
            financials = dat.financials.T.reset_index()
            financials = financials.rename(columns={'index': 'Date'})
            financials['stock_symbol'] = ticker.split('.NS')[0]
            
            logger.info(f"Retrieved financial statements for {ticker}: {len(financials)} records")
            return financials
            
        except Exception as e:
            logger.error(f"Error getting financial statements for {ticker}: {str(e)}")
            return None
    
    def get_balance_sheet(self, ticker: str) -> Optional[pd.DataFrame]:
        """Get balance sheet data"""
        try:
            dat = self.get_ticker_data(ticker)
            if dat is None:
                return None
            
            balance_sheet = dat.balance_sheet.T.reset_index()
            balance_sheet = balance_sheet.rename(columns={'index': 'Date'})
            balance_sheet['stock_symbol'] = ticker.split('.NS')[0]
            
            logger.info(f"Retrieved balance sheet for {ticker}: {len(balance_sheet)} records")
            return balance_sheet
            
        except Exception as e:
            logger.error(f"Error getting balance sheet for {ticker}: {str(e)}")
            return None
    
    def get_income_statement(self, ticker: str) -> Optional[pd.DataFrame]:
        """Get income statement data"""
        try:
            dat = self.get_ticker_data(ticker)
            if dat is None:
                return None
            
            income_stmt = dat.income_stmt.T.reset_index()
            income_stmt = income_stmt.rename(columns={'index': 'Date'})
            income_stmt['stock_symbol'] = ticker.split('.NS')[0]
            
            logger.info(f"Retrieved income statement for {ticker}: {len(income_stmt)} records")
            return income_stmt
            
        except Exception as e:
            logger.error(f"Error getting income statement for {ticker}: {str(e)}")
            return None
    
    def get_cash_flow_statement(self, ticker: str) -> Optional[pd.DataFrame]:
        """Get cash flow statement data"""
        try:
            dat = self.get_ticker_data(ticker)
            if dat is None:
                return None
            
            cash_flow = dat.cash_flow.T.reset_index()
            cash_flow = cash_flow.rename(columns={'index': 'Date'})
            cash_flow['stock_symbol'] = ticker.split('.NS')[0]
            
            logger.info(f"Retrieved cash flow statement for {ticker}: {len(cash_flow)} records")
            return cash_flow
            
        except Exception as e:
            logger.error(f"Error getting cash flow statement for {ticker}: {str(e)}")
            return None
    
    def get_daily_price_history(self, ticker: str) -> Optional[pd.DataFrame]:
        """Get 10 years daily price history"""
        try:
            dat = self.get_ticker_data(ticker)
            if dat is None:
                return None
            
            hist = dat.history(period='10y', interval='1d', auto_adjust=False).reset_index()
            hist['stock_symbol'] = ticker.split('.NS')[0]
            
            logger.info(f"Retrieved daily price history for {ticker}: {len(hist)} records")
            return hist
            
        except Exception as e:
            logger.error(f"Error getting daily price history for {ticker}: {str(e)}")
            return None
    
    def get_monthly_price_history(self, ticker: str) -> Optional[pd.DataFrame]:
        """Get monthly price history from daily data"""
        try:
            hist = self.get_daily_price_history(ticker)
            if hist is None:
                return None
            
            hist['year'] = hist['Date'].dt.year
            hist['month'] = hist['Date'].dt.month
            
            def stockwise_monthly_gp_fn(gp):
                gp1 = gp.sort_values(by='Date', ascending=False)
                gp2 = gp1.iloc[0, :][['stock_symbol', 'Date', 'Close']]
                return gp2
            
            monthly_hist = hist.groupby(by=['stock_symbol', 'year', 'month']).apply(
                lambda gp: stockwise_monthly_gp_fn(gp)
            ).reset_index(drop=True)
            
            # Rename Close column to match expected database structure
            monthly_hist = monthly_hist.rename(columns={'Close': 'Adjusted_Monthly_Close_Price'})
            
            logger.info(f"Processed monthly price history for {ticker}: {len(monthly_hist)} records")
            return monthly_hist
            
        except Exception as e:
            logger.error(f"Error processing monthly price history for {ticker}: {str(e)}")
            return None
    
    def get_intrinsic_pe_data(self, ticker: str) -> Optional[pd.DataFrame]:
        """Calculate intrinsic PE ratio data"""
        try:
            # Get monthly price history
            monthly_hist = self.get_monthly_price_history(ticker)
            if monthly_hist is None:
                return None
            
            # Get financial statements for EPS data
            financials = self.get_financial_statements(ticker)
            if financials is None:
                return None
            
            current_financial_year = self.get_current_financial_year()
            stock_symbol = ticker.split('.NS')[0]
            
            # Process monthly data for yearly averages
            monthly_hist['year'] = monthly_hist['Date'].dt.year
            monthly_hist['month'] = monthly_hist['Date'].dt.month
            monthly_hist['financial_year'] = monthly_hist.apply(
                lambda row: row['year'] if row['month'] >= self.financial_year_start_month else row['year'] - 1,
                axis=1
            )
            
            def stockwise_yearly_gp_fn(gp):
                gp['Avg_Price'] = gp['Adjusted_Monthly_Close_Price'].mean().round(2)
                gp1 = gp.sort_values(by='Date', ascending=False).iloc[0, :][
                    ['stock_symbol', 'Date', 'financial_year', 'Avg_Price']
                ]
                return gp1
            
            yearly_hist_avg = monthly_hist.groupby(by=['stock_symbol', 'financial_year']).apply(
                lambda gp: stockwise_yearly_gp_fn(gp)
            ).reset_index(drop=True)
            
            # Process financial data for EPS
            fin = financials[['stock_symbol', 'Date', 'Basic EPS']].copy()
            fin = fin.rename(columns={'Basic EPS': 'EPS'})
            fin['year'] = fin['Date'].dt.year
            fin['month'] = fin['Date'].dt.month
            fin['financial_year'] = fin.apply(
                lambda row: row['year'] if row['month'] >= 4 else row['year'] - 1,
                axis=1
            )
            fin = fin[['stock_symbol', 'financial_year', 'EPS']]
            
            # Merge price and EPS data
            intrinsic_pe = pd.merge(yearly_hist_avg, fin, on=['stock_symbol', 'financial_year'], how='left')
            
            # Exclude current financial year
            intrinsic_pe = intrinsic_pe[intrinsic_pe['financial_year'] != current_financial_year]
            
            # Calculate PE ratio
            intrinsic_pe['PE_Ratio'] = (intrinsic_pe['Avg_Price'] / intrinsic_pe['EPS']).astype(float).round(2)
            
            logger.info(f"Calculated intrinsic PE data for {ticker}: {len(intrinsic_pe)} records")
            return intrinsic_pe
            
        except Exception as e:
            logger.error(f"Error calculating intrinsic PE data for {ticker}: {str(e)}")
            return None
    
    def get_sector_info_from_moneycontrol(self, stock_symbol: str) -> Optional[Dict[str, Any]]:
        """Get sector and sector PE from MoneyControl API"""
        try:
            url = f"https://priceapi.moneycontrol.com/pricefeed/bse/equitycash/{stock_symbol}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            sector_info = {
                'Sector': data.get('sector', ''),
                'Sector_PE': data.get('sectorPE', None)
            }
            
            logger.info(f"Retrieved sector info for {stock_symbol}: {sector_info}")
            return sector_info
            
        except Exception as e:
            logger.error(f"Error getting sector info from MoneyControl for {stock_symbol}: {str(e)}")
            return None

# Global financial data manager instance
financial_data_manager = FinancialDataManager() 