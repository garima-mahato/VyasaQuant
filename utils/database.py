import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import os
from typing import Optional, Dict, Any
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for PostgreSQL operations"""
    
    def __init__(self):
        self.connection_string = self._get_connection_string()
        self.engine = None
        
    def _get_connection_string(self) -> str:
        """Get database connection string from environment variables"""
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'postgres')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', 'postgres')
        
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    def get_engine(self):
        """Get SQLAlchemy engine"""
        if self.engine is None:
            self.engine = create_engine(self.connection_string)
        return self.engine
    
    def get_connection(self):
        """Get direct psycopg2 connection"""
        return psycopg2.connect(self.connection_string)
    
    def insert_dataframe(self, df: pd.DataFrame, table_name: str, if_exists: str = 'append') -> bool:
        """Insert pandas DataFrame into PostgreSQL table"""
        try:
            engine = self.get_engine()
            df.to_sql(table_name, engine, if_exists=if_exists, index=False)
            logger.info(f"Successfully inserted {len(df)} rows into {table_name}")
            return True
        except Exception as e:
            logger.error(f"Error inserting data into {table_name}: {str(e)}")
            return False
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[pd.DataFrame]:
        """Execute a SELECT query and return results as DataFrame"""
        try:
            engine = self.get_engine()
            return pd.read_sql_query(query, engine, params=params)
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return None
    
    def execute_update(self, query: str, params: tuple = None) -> bool:
        """Execute an UPDATE/INSERT/DELETE query"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error executing update: {str(e)}")
            return False
    
    def upsert_stock_data(self, stock_data: Dict[str, Any]) -> bool:
        """Upsert stock data into vq_tbl_stock table"""
        query = """
        INSERT INTO vq_tbl_stock (stock_symbol, "Stock_Name", "Ticker", "Sector", "Current_Financial_Year", "Sector_PE")
        VALUES (%(stock_symbol)s, %(Stock_Name)s, %(Ticker)s, %(Sector)s, %(Current_Financial_Year)s, %(Sector_PE)s)
        ON CONFLICT (stock_symbol) 
        DO UPDATE SET 
            "Stock_Name" = EXCLUDED."Stock_Name",
            "Ticker" = EXCLUDED."Ticker",
            "Sector" = EXCLUDED."Sector",
            "Current_Financial_Year" = EXCLUDED."Current_Financial_Year",
            "Sector_PE" = EXCLUDED."Sector_PE",
            updated_at = CURRENT_TIMESTAMP
        """
        return self.execute_update(query, stock_data)
    
    def update_stock_field(self, stock_symbol: str, field_name: str, value: Any) -> bool:
        """Update a specific field for a stock"""
        query = f'UPDATE vq_tbl_stock SET "{field_name}" = %s, updated_at = CURRENT_TIMESTAMP WHERE stock_symbol = %s'
        return self.execute_update(query, (value, stock_symbol))

# Global database manager instance
db_manager = DatabaseManager() 