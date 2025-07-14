import pandas as pd
import os
from typing import Optional
import logging
from pathlib import Path

# Configure file logging for ticker_utils
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

logger = logging.getLogger(__name__)

# Add file handler if not already present
if not any(isinstance(handler, logging.FileHandler) for handler in logger.handlers):
    file_handler = logging.FileHandler(log_dir / "ticker_utils.log", encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)

class TickerManager:
    """Manager for ticker symbol operations"""
    
    def __init__(self, csv_path: str = None):
        if csv_path is None:
            # Use absolute path relative to project root
            project_root = Path(__file__).parent.parent  # Go up from utils/ to project root
            csv_path = str(project_root / "data" / "indian_equities_ticker_database.csv")
        
        self.csv_path = csv_path
        self._ticker_df = None
    
    def _load_ticker_data(self) -> pd.DataFrame:
        """Load ticker data from CSV file"""
        if self._ticker_df is None:
            try:
                if not os.path.exists(self.csv_path):
                    raise FileNotFoundError(f"Ticker database file not found: {self.csv_path}")
                
                self._ticker_df = pd.read_csv(self.csv_path)
                logger.info(f"Loaded {len(self._ticker_df)} ticker records from {self.csv_path}")
            except Exception as e:
                logger.error(f"Error loading ticker data: {str(e)}")
                raise
        
        return self._ticker_df
    
    def get_symbol_by_name(self, company_name: str) -> Optional[str]:
        """
        Get ticker symbol by company name.
        
        Args:
            company_name: Name of the company to search for
            
        Returns:
            Ticker symbol if found, None otherwise
        """
        try:
            logger.info(f"TickerManager: Looking up symbol for '{company_name}'")
            
            df = self._load_ticker_data()
            if df is None:
                logger.error("TickerManager: Ticker data not loaded")
                return None
            
            logger.info(f"TickerManager: Loaded {len(df)} ticker records")
            
            # Clean the input
            company_name = company_name.strip()
            logger.info(f"TickerManager: Cleaned company name: '{company_name}'")
            
            # Try exact match first (case-insensitive)
            logger.info("TickerManager: Trying exact match...")
            exact_match = df[df['name'].str.lower() == company_name.lower()]
            
            if not exact_match.empty:
                symbol = exact_match.iloc[0]['symbol']
                logger.info(f"TickerManager: Found exact match - Symbol: {symbol}")
                return symbol
            
            logger.info("TickerManager: No exact match found, trying partial match...")
            # Try partial match
            partial_match = df[df['name'].str.contains(company_name, case=False, na=False)]
            
            if not partial_match.empty:
                symbol = partial_match.iloc[0]['symbol']
                logger.info(f"TickerManager: Found partial match - Symbol: {symbol}")
                return symbol
            
            logger.warning(f"TickerManager: No matches found for '{company_name}'")
            
            # Debug: Show some sample company names for reference
            sample_names = df['name'].head(10).tolist()
            logger.info(f"TickerManager: Sample company names in database: {sample_names}")
            
            return None
            
        except Exception as e:
            logger.error(f"TickerManager: Error in get_symbol_by_name: {str(e)}")
            import traceback
            logger.error(f"TickerManager: Traceback: {traceback.format_exc()}")
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