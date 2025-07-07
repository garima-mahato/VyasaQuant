"""
Moneycontrol Data Source
Handles data fetching from Moneycontrol.com - India's leading financial portal.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


class MoneycontrolDataSource:
    """Data source for Moneycontrol financial data and news"""
    
    def __init__(self):
        self.base_url = "https://www.moneycontrol.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_stock_url(self, symbol: str) -> Optional[str]:
        """Search for stock URL on Moneycontrol"""
        try:
            search_url = f"{self.base_url}/stocks/cptmarket/compsearchnew.php"
            params = {
                'search_data': symbol,
                'cid': '1'
            }
            
            response = self.session.get(search_url, params=params)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find the first stock link
                stock_links = soup.find_all('a', href=re.compile(r'/stocks/marketstats/'))
                
                if stock_links:
                    return self.base_url + stock_links[0]['href']
                
            return None
        except Exception as e:
            logger.error(f"Error searching Moneycontrol URL for {symbol}: {e}")
            return None
    
    def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """Get stock quote from Moneycontrol"""
        try:
            stock_url = self.search_stock_url(symbol)
            
            if not stock_url:
                return {}
            
            response = self.session.get(stock_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                quote_data = {
                    'symbol': symbol,
                    'source': 'Moneycontrol',
                    'url': stock_url
                }
                
                # Extract current price
                price_element = soup.find('span', {'id': 'Bse_Prc_tick'})
                if price_element:
                    quote_data['current_price'] = price_element.get_text().strip()
                
                # Extract change and percentage change
                change_element = soup.find('span', {'id': 'Bse_Prc_tick_change'})
                if change_element:
                    quote_data['change'] = change_element.get_text().strip()
                
                return quote_data
            else:
                logger.error(f"Failed to fetch Moneycontrol data for {symbol}")
                return {}
        except Exception as e:
            logger.error(f"Error fetching Moneycontrol quote for {symbol}: {e}")
            return {}
    
    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """Get detailed company information from Moneycontrol"""
        try:
            stock_url = self.search_stock_url(symbol)
            
            if not stock_url:
                return {}
            
            # Navigate to company info page
            info_url = stock_url.replace('/marketstats/', '/company-facts/')
            response = self.session.get(info_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                company_info = {
                    'symbol': symbol,
                    'source': 'Moneycontrol'
                }
                
                # Extract basic company details
                # This would need to be implemented based on Moneycontrol's HTML structure
                
                return company_info
            else:
                logger.error(f"Failed to fetch Moneycontrol company info for {symbol}")
                return {}
        except Exception as e:
            logger.error(f"Error fetching Moneycontrol company info for {symbol}: {e}")
            return {}
    
    def get_financial_ratios(self, symbol: str) -> Dict[str, Any]:
        """Get financial ratios from Moneycontrol"""
        try:
            stock_url = self.search_stock_url(symbol)
            
            if not stock_url:
                return {}
            
            # Navigate to ratios page
            ratios_url = stock_url.replace('/marketstats/', '/ratios/')
            response = self.session.get(ratios_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                ratios_data = {
                    'symbol': symbol,
                    'source': 'Moneycontrol'
                }
                
                # Extract financial ratios
                # This would need to be implemented based on Moneycontrol's HTML structure
                
                return ratios_data
            else:
                logger.error(f"Failed to fetch Moneycontrol ratios for {symbol}")
                return {}
        except Exception as e:
            logger.error(f"Error fetching Moneycontrol ratios for {symbol}: {e}")
            return {}
    
    def get_news(self, symbol: str, num_articles: int = 10) -> List[Dict[str, Any]]:
        """Get latest news for a stock from Moneycontrol"""
        try:
            news_url = f"{self.base_url}/news/tags/{symbol.lower()}.html"
            response = self.session.get(news_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                news_articles = []
                
                # Find news articles
                articles = soup.find_all('li', class_='clearfix')[:num_articles]
                
                for article in articles:
                    title_element = article.find('a')
                    if title_element:
                        news_articles.append({
                            'title': title_element.get_text().strip(),
                            'url': self.base_url + title_element['href'],
                            'source': 'Moneycontrol',
                            'symbol': symbol,
                            'timestamp': datetime.now().isoformat()
                        })
                
                return news_articles
            else:
                logger.error(f"Failed to fetch Moneycontrol news for {symbol}")
                return []
        except Exception as e:
            logger.error(f"Error fetching Moneycontrol news for {symbol}: {e}")
            return []
    
    def get_sector_analysis(self, sector: str) -> Dict[str, Any]:
        """Get sector analysis from Moneycontrol"""
        try:
            sector_url = f"{self.base_url}/stocks/sectors/{sector.lower()}"
            response = self.session.get(sector_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                sector_data = {
                    'sector': sector,
                    'source': 'Moneycontrol',
                    'url': sector_url
                }
                
                # Extract sector performance data
                # This would need to be implemented based on Moneycontrol's HTML structure
                
                return sector_data
            else:
                logger.error(f"Failed to fetch Moneycontrol sector analysis for {sector}")
                return {}
        except Exception as e:
            logger.error(f"Error fetching Moneycontrol sector analysis for {sector}: {e}")
            return {}
    
    def get_mutual_fund_holdings(self, symbol: str) -> List[Dict[str, Any]]:
        """Get mutual fund holdings data for a stock"""
        try:
            # This would need to be implemented based on Moneycontrol's structure
            # for mutual fund holdings data
            
            holdings_data = []
            
            return holdings_data
        except Exception as e:
            logger.error(f"Error fetching Moneycontrol MF holdings for {symbol}: {e}")
            return [] 