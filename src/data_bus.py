"""
Adobe Data Bus Module
Handles real-time data streaming and processing from multiple sources.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import time
from ib_insync import IB, Stock, Option, util
import requests
from newsapi import NewsApiClient
from fredapi import Fred
from dotenv import load_dotenv
import os

load_dotenv()

class AdobeDataBus:
    def __init__(self, paper_trading: bool = True):
        # Initialize API clients
        self.ib = IB()
        self.newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))
        self.fred = Fred(api_key=os.getenv('FRED_API_KEY'))
        
        # Paper trading configuration
        self.paper_trading = paper_trading
        self.gateway_host = os.getenv('IBKR_HOST', '127.0.0.1')
        self.gateway_port = int(os.getenv('IBKR_PORT', '7497'))
        self.client_id = int(os.getenv('IBKR_CLIENT_ID', '1'))
        
        # ADBE-specific configuration
        self.symbol = 'ADBE'
        self.sector = 'Technology'
        self.industry = 'Software'
        self.peers = ['CRM', 'NOW', 'WDAY', 'INTU', 'MSFT']
        
        # Data buffers
        self.options_buffer = []
        self.news_buffer = []
        self.fundamental_buffer = {}
        self.macro_buffer = {}
        
        # Update timestamps
        self.last_update = {
            'options': datetime.min,
            'news': datetime.min,
            'fundamental': datetime.min,
            'macro': datetime.min
        }
        
        # Connect to IBKR Gateway
        self._connect_to_gateway()
    
    def _connect_to_gateway(self):
        """Connect to IBKR Gateway"""
        try:
            # Connect to Gateway
            self.ib.connect(
                self.gateway_host,
                self.gateway_port,
                clientId=self.client_id,
                readonly=False
            )
            
            # Set paper trading mode if enabled
            if self.paper_trading:
                self.ib.reqGlobalCancel()  # Cancel any existing orders
                logging.info(f"Connected to IBKR Gateway at {self.gateway_host}:{self.gateway_port} in PAPER TRADING mode")
            else:
                logging.info(f"Connected to IBKR Gateway at {self.gateway_host}:{self.gateway_port} in LIVE TRADING mode")
                
        except Exception as e:
            logging.error(f"Failed to connect to IBKR Gateway: {str(e)}")
            raise
    
    def get_market_data(self) -> Dict[str, Any]:
        """Get current market data"""
        try:
            # Get stock data
            stock = Stock(self.symbol)
            self.ib.qualifyContracts(stock)
            
            # Request market data
            self.ib.reqMktData(stock)
            time.sleep(1)  # Wait for data
            
            # Get options chain
            chains = self.ib.reqSecDefOptParams(stock.symbol, '', stock.secType, stock.conId)
            time.sleep(1)  # Wait for data
            
            # Process market data
            market_data = {
                'symbol': self.symbol,
                'price': stock.last,
                'volume': stock.volume,
                'bid': stock.bid,
                'ask': stock.ask,
                'iv_rank': self._calculate_iv_rank(chains),
                'timestamp': datetime.now().isoformat()
            }
            
            return market_data
            
        except Exception as e:
            logging.error(f"Error getting market data: {str(e)}")
            return {}
    
    def get_options_data(self) -> Dict[str, Any]:
        """Get options data"""
        try:
            # Get stock data
            stock = Stock(self.symbol)
            self.ib.qualifyContracts(stock)
            
            # Get options chain
            chains = self.ib.reqSecDefOptParams(stock.symbol, '', stock.secType, stock.conId)
            time.sleep(1)  # Wait for data
            
            # Process options data
            options_data = {
                'symbol': self.symbol,
                'expirations': [chain.expirations for chain in chains],
                'strikes': [chain.strikes for chain in chains],
                'call_put_ratio': self._calculate_call_put_ratio(chains),
                'volume_profile': self._calculate_volume_profile(chains),
                'timestamp': datetime.now().isoformat()
            }
            
            return options_data
            
        except Exception as e:
            logging.error(f"Error getting options data: {str(e)}")
            return {}
    
    def get_news_data(self) -> Dict[str, Any]:
        """Get news data"""
        try:
            # Get news from NewsAPI
            news = self.newsapi.get_everything(
                q=f'"{self.symbol}" OR "Adobe"',
                language='en',
                sort_by='relevancy',
                page_size=10
            )
            
            # Process news data
            news_data = {
                'symbol': self.symbol,
                'articles': news['articles'],
                'overall_sentiment': self._calculate_news_sentiment(news['articles']),
                'recent_headlines': [article['title'] for article in news['articles']],
                'timestamp': datetime.now().isoformat()
            }
            
            return news_data
            
        except Exception as e:
            logging.error(f"Error getting news data: {str(e)}")
            return {}
    
    def get_fundamental_data(self) -> Dict[str, Any]:
        """Get fundamental data"""
        try:
            # Get stock data
            stock = Stock(self.symbol)
            self.ib.qualifyContracts(stock)
            
            # Request fundamental data
            self.ib.reqFundamentalData(stock, 'ReportSnapshot')
            time.sleep(1)  # Wait for data
            
            # Process fundamental data
            fundamental_data = {
                'symbol': self.symbol,
                'pe_ratio': stock.peRatio,
                'eps': stock.eps,
                'market_cap': stock.marketCap,
                'sector': self.sector,
                'industry': self.industry,
                'peers': self.peers,
                'timestamp': datetime.now().isoformat()
            }
            
            return fundamental_data
            
        except Exception as e:
            logging.error(f"Error getting fundamental data: {str(e)}")
            return {}
    
    def get_macro_data(self) -> Dict[str, Any]:
        """Get macroeconomic data"""
        try:
            # Get macro indicators
            indicators = {
                'GDP': self.fred.get_series('GDP'),
                'UNRATE': self.fred.get_series('UNRATE'),
                'CPIAUCSL': self.fred.get_series('CPIAUCSL'),
                'FEDFUNDS': self.fred.get_series('FEDFUNDS')
            }
            
            # Process macro data
            macro_data = {
                'gdp': indicators['GDP'].iloc[-1],
                'unemployment': indicators['UNRATE'].iloc[-1],
                'inflation': indicators['CPIAUCSL'].iloc[-1],
                'fed_funds': indicators['FEDFUNDS'].iloc[-1],
                'timestamp': datetime.now().isoformat()
            }
            
            return macro_data
            
        except Exception as e:
            logging.error(f"Error getting macro data: {str(e)}")
            return {}
    
    def _calculate_iv_rank(self, chains: List[Any]) -> float:
        """Calculate IV rank"""
        try:
            # Implement IV rank calculation
            return 0.0
        except Exception as e:
            logging.error(f"Error calculating IV rank: {str(e)}")
            return 0.0
    
    def _calculate_call_put_ratio(self, chains: List[Any]) -> float:
        """Calculate call/put ratio"""
        try:
            # Implement call/put ratio calculation
            return 0.0
        except Exception as e:
            logging.error(f"Error calculating call/put ratio: {str(e)}")
            return 0.0
    
    def _calculate_volume_profile(self, chains: List[Any]) -> Dict[str, Any]:
        """Calculate volume profile"""
        try:
            # Implement volume profile calculation
            return {}
        except Exception as e:
            logging.error(f"Error calculating volume profile: {str(e)}")
            return {}
    
    def _calculate_news_sentiment(self, articles: List[Dict[str, Any]]) -> float:
        """Calculate news sentiment"""
        try:
            # Implement news sentiment calculation
            return 0.0
        except Exception as e:
            logging.error(f"Error calculating news sentiment: {str(e)}")
            return 0.0
    
    def update_stream(self) -> Dict[str, Any]:
        """Update all data streams"""
        try:
            # Check connection status
            if not self.ib.isConnected():
                logging.warning("Connection lost, attempting to reconnect...")
                self._connect_to_gateway()
            
            current_time = datetime.now()
            
            # Update options data every 5 minutes
            if (current_time - self.last_update['options']).seconds >= 300:
                self._update_options_data()
                self.last_update['options'] = current_time
            
            # Update news data every 15 minutes
            if (current_time - self.last_update['news']).seconds >= 900:
                self._update_news_data()
                self.last_update['news'] = current_time
            
            # Update fundamental data every hour
            if (current_time - self.last_update['fundamental']).seconds >= 3600:
                self._update_fundamental_data()
                self.last_update['fundamental'] = current_time
            
            # Update macro data every 4 hours
            if (current_time - self.last_update['macro']).seconds >= 14400:
                self._update_macro_data()
                self.last_update['macro'] = current_time
            
            return {
                'status': 'success',
                'last_updates': self.last_update,
                'buffer_sizes': {
                    'options': len(self.options_buffer),
                    'news': len(self.news_buffer),
                    'fundamental': len(self.fundamental_buffer),
                    'macro': len(self.macro_buffer)
                }
            }
            
        except Exception as e:
            logging.error(f"Error updating data streams: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _update_options_data(self):
        """Update options chain data from IBKR"""
        try:
            # Get ADBE stock contract
            stock = Stock(self.symbol, 'SMART', 'USD')
            
            # Get options chain
            chains = self.ib.reqSecDefOptParams(stock.symbol, '', stock.secType, stock.conId)
            
            for chain in chains:
                # Get options for each expiration
                strikes = [strike for strike in chain.strikes if 0.7 <= strike/stock.price <= 1.3]
                expirations = [exp for exp in chain.expirations if exp > datetime.now()]
                
                for exp in expirations[:3]:  # Get next 3 expirations
                    for strike in strikes:
                        # Get call option
                        call = Option(self.symbol, exp, strike, 'C', 'SMART', 'USD')
                        self.ib.qualifyContracts(call)
                        self.ib.reqMktData(call)
                        
                        # Get put option
                        put = Option(self.symbol, exp, strike, 'P', 'SMART', 'USD')
                        self.ib.qualifyContracts(put)
                        self.ib.reqMktData(put)
                        
                        # Wait for data
                        self.ib.sleep(1)
                        
                        # Store data
                        if call.contract and call.marketPrice():
                            self.options_buffer.append({
                                'timestamp': datetime.now(),
                                'type': 'call',
                                'strike': strike,
                                'expiry': exp,
                                'price': call.marketPrice(),
                                'volume': call.volume,
                                'open_interest': call.openInterest
                            })
                        
                        if put.contract and put.marketPrice():
                            self.options_buffer.append({
                                'timestamp': datetime.now(),
                                'type': 'put',
                                'strike': strike,
                                'expiry': exp,
                                'price': put.marketPrice(),
                                'volume': put.volume,
                                'open_interest': put.openInterest
                            })
            
            # Keep only last 1000 records
            self.options_buffer = self.options_buffer[-1000:]
            
        except Exception as e:
            logging.error(f"Error updating options data: {str(e)}")
    
    def _update_news_data(self):
        """Update news data from NewsAPI"""
        try:
            # Get news for ADBE
            news = self.newsapi.get_everything(
                q=f'"{self.symbol}" OR "Adobe"',
                language='en',
                sort_by='relevancy',
                page_size=50
            )
            
            # Process and store news
            for article in news['articles']:
                self.news_buffer.append({
                    'timestamp': datetime.strptime(article['publishedAt'], '%Y-%m-%dT%H:%M:%SZ'),
                    'title': article['title'],
                    'description': article['description'],
                    'url': article['url'],
                    'source': article['source']['name']
                })
            
            # Keep only last 100 records
            self.news_buffer = self.news_buffer[-100:]
            
        except Exception as e:
            logging.error(f"Error updating news data: {str(e)}")
    
    def _update_fundamental_data(self):
        """Update fundamental data from FMP"""
        try:
            # Get fundamental data
            url = f"https://financialmodelingprep.com/api/v3/quote/{self.symbol}?apikey={os.getenv('FMP_API_KEY')}"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()[0]
            
            self.fundamental_buffer = {
                'timestamp': datetime.now(),
                'price': data.get('price', 0),
                'volume': data.get('volume', 0),
                'market_cap': data.get('marketCap', 0),
                'pe_ratio': data.get('pe', 0),
                'eps': data.get('eps', 0),
                'dividend': data.get('dividend', 0)
            }
            
        except Exception as e:
            logging.error(f"Error updating fundamental data: {str(e)}")
    
    def _update_macro_data(self):
        """Update macroeconomic data from FRED"""
        try:
            # Get relevant macro indicators
            indicators = {
                'GDP': 'GDP',
                'UNRATE': 'UNRATE',
                'CPIAUCSL': 'CPIAUCSL',
                'FEDFUNDS': 'FEDFUNDS'
            }
            
            for code, series in indicators.items():
                data = self.fred.get_series(series, observation_start=datetime.now() - timedelta(days=30))
                self.macro_buffer[code] = {
                    'timestamp': datetime.now(),
                    'value': data.iloc[-1],
                    'change': data.iloc[-1] - data.iloc[-2]
                }
            
        except Exception as e:
            logging.error(f"Error updating macro data: {str(e)}")
    
    def get_latest_data(self) -> Dict[str, Any]:
        """Get the latest data from all buffers"""
        return {
            'options': self.options_buffer[-1] if self.options_buffer else None,
            'news': self.news_buffer[-1] if self.news_buffer else None,
            'fundamental': self.fundamental_buffer,
            'macro': self.macro_buffer
        }
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.ib.isConnected():
                self.ib.disconnect()
                logging.info("Disconnected from IBKR Gateway")
        except Exception as e:
            logging.error(f"Error during cleanup: {str(e)}") 