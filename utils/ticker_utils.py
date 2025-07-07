import pandas as pd
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class TickerManager:
    """Manager for ticker symbol operations"""
    
    def __init__(self, csv_path: str = "data/indian_equities_ticker_database.csv"):
        self.csv_path = csv_path
        self._ticker_df = None
    
    def _load_ticker_data(self) -> pd.DataFrame:
        """Load ticker data from CSV file"""
        if self._ticker_df is None:
            try:
                if not os.path.exists(self.csv_path):
                    raise FileNotFoundError(f"Ticker database file not found: {self.csv_path}")
                
                self._ticker_df = pd.read_csv(self.csv_path)
                logger.info(f"Loaded {len(self._ticker_df)} ticker records")
            except Exception as e:
                logger.error(f"Error loading ticker data: {str(e)}")
                raise
        
        return self._ticker_df
    
    def get_symbol_by_name(self, company_name: str) -> Optional[str]:
        """
        Get ticker symbol by company name
        
        Args:
            company_name: Name of the company to search for
            
        Returns:
            Ticker symbol if found, None otherwise
        """
        try:
            df = self._load_ticker_data()
            
            # First try exact match (case insensitive)
            exact_match = df[df['name'].str.lower() == company_name.lower()]
            if not exact_match.empty:
                symbol = exact_match.iloc[0]['symbol']
                logger.info(f"Found exact match for '{company_name}': {symbol}")
                return symbol
            
            # Try partial match
            partial_match = df[df['name'].str.contains(company_name.strip(), case=False, na=False)]
            if not partial_match.empty:
                symbol = partial_match.iloc[0]['symbol']
                matched_name = partial_match.iloc[0]['name']
                logger.info(f"Found partial match for '{company_name}': {symbol} ({matched_name})")
                return symbol
            
            # Try reverse partial match (search company name in each record)
            for _, row in df.iterrows():
                if company_name.lower().strip() in row['name'].lower():
                    symbol = row['symbol']
                    logger.info(f"Found reverse match for '{company_name}': {symbol} ({row['name']})")
                    return symbol
            
            logger.warning(f"No ticker symbol found for company: {company_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error searching for ticker symbol: {str(e)}")
            return None
    
    def get_company_info(self, symbol: str) -> Optional[dict]:
        """
        Get company information by ticker symbol
        
        Args:
            symbol: Ticker symbol
            
        Returns:
            Dictionary with company information if found, None otherwise
        """
        try:
            df = self._load_ticker_data()
            
            # Search for the symbol
            company_data = df[df['symbol'] == symbol]
            if not company_data.empty:
                return company_data.iloc[0].to_dict()
            
            logger.warning(f"No company information found for symbol: {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting company info: {str(e)}")
            return None
    
    def search_companies(self, search_term: str, limit: int = 10) -> list:
        """
        Search for companies by name or symbol
        
        Args:
            search_term: Term to search for
            limit: Maximum number of results
            
        Returns:
            List of dictionaries with company information
        """
        try:
            df = self._load_ticker_data()
            
            # Search in both name and symbol columns
            matches = df[
                (df['name'].str.contains(search_term, case=False, na=False)) |
                (df['symbol'].str.contains(search_term, case=False, na=False))
            ]
            
            results = matches.head(limit).to_dict('records')
            logger.info(f"Found {len(results)} matches for search term: {search_term}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching companies: {str(e)}")
            return []

# Global ticker manager instance
ticker_manager = TickerManager() 