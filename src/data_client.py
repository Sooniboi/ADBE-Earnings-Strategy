"""
Data Client Module
Handles fetching and processing data from various sources including FMP.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv
import os

load_dotenv()

class DataClient:
    def __init__(self):
        self.fmp_api_key = os.getenv('FMP_API_KEY')
        self.base_url = "https://financialmodelingprep.com/api/v3"
        self.symbol = "ORCL"
        
    def get_earnings_history(self) -> Dict[str, Any]:
        """Get earnings history for the last 3 years"""
        try:
            # Calculate date 3 years ago
            three_years_ago = datetime.now() - timedelta(days=3*365)
            from_date = three_years_ago.strftime('%Y-%m-%d')
            
            url = f"{self.base_url}/historical/earning_calendar/{self.symbol}?apikey={self.fmp_api_key}"
            response = requests.get(url)
            response.raise_for_status()
            
            earnings_data = response.json()
            
            # Filter for last 3 years
            filtered_earnings = [
                earning for earning in earnings_data 
                if datetime.strptime(earning['date'], '%Y-%m-%d') >= three_years_ago
            ]
            
            return {
                "has_history": True,
                "earnings": filtered_earnings,
                "summary": f"Found {len(filtered_earnings)} earnings reports in the last 3 years"
            }
            
        except Exception as e:
            logging.error(f"Error fetching earnings history: {str(e)}")
            return {
                "has_history": False,
                "summary": f"Error fetching earnings history: {str(e)}"
            }
    
    def get_options_data(self) -> Dict[str, Any]:
        """Get current options data"""
        try:
            url = f"{self.base_url}/quote/{self.symbol}?apikey={self.fmp_api_key}"
            response = requests.get(url)
            response.raise_for_status()
            
            quote_data = response.json()[0]
            
            # Get options chain
            options_url = f"{self.base_url}/options/{self.symbol}?apikey={self.fmp_api_key}"
            options_response = requests.get(options_url)
            options_response.raise_for_status()
            
            options_data = options_response.json()
            
            return {
                "has_options_data": True,
                "current_price": quote_data.get('price', 0),
                "options_chain": options_data,
                "summary": f"Retrieved options data for {self.symbol}"
            }
            
        except Exception as e:
            logging.error(f"Error fetching options data: {str(e)}")
            return {
                "has_options_data": False,
                "summary": f"Error fetching options data: {str(e)}"
            }
    
    def get_volume_data(self) -> Dict[str, Any]:
        """Get volume data for the last 3 years"""
        try:
            # Calculate date 3 years ago
            three_years_ago = datetime.now() - timedelta(days=3*365)
            from_date = three_years_ago.strftime('%Y-%m-%d')
            
            url = f"{self.base_url}/historical-price-full/{self.symbol}?from={from_date}&apikey={self.fmp_api_key}"
            response = requests.get(url)
            response.raise_for_status()
            
            historical_data = response.json()
            
            return {
                "has_volume_data": True,
                "historical_volume": historical_data.get('historical', []),
                "summary": f"Retrieved volume data for {self.symbol} from {from_date}"
            }
            
        except Exception as e:
            logging.error(f"Error fetching volume data: {str(e)}")
            return {
                "has_volume_data": False,
                "summary": f"Error fetching volume data: {str(e)}"
            }
    
    def get_market_data(self) -> Dict[str, Any]:
        """Get current market data"""
        try:
            url = f"{self.base_url}/quote/{self.symbol}?apikey={self.fmp_api_key}"
            response = requests.get(url)
            response.raise_for_status()
            
            market_data = response.json()[0]
            
            return {
                "has_market_data": True,
                "data": market_data,
                "summary": f"Retrieved market data for {self.symbol}"
            }
            
        except Exception as e:
            logging.error(f"Error fetching market data: {str(e)}")
            return {
                "has_market_data": False,
                "summary": f"Error fetching market data: {str(e)}"
            }
    
    def get_news_data(self) -> Dict[str, Any]:
        """Get recent news data"""
        try:
            url = f"{self.base_url}/stock_news?tickers={self.symbol}&limit=50&apikey={self.fmp_api_key}"
            response = requests.get(url)
            response.raise_for_status()
            
            news_data = response.json()
            
            return {
                "has_news_data": True,
                "news": news_data,
                "summary": f"Retrieved {len(news_data)} news articles for {self.symbol}"
            }
            
        except Exception as e:
            logging.error(f"Error fetching news data: {str(e)}")
            return {
                "has_news_data": False,
                "summary": f"Error fetching news data: {str(e)}"
            } 