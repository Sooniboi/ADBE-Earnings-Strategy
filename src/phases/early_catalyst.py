"""
Early Catalyst Phase Module
Handles analysis and trading decisions for the early catalyst phase.
"""

import logging
from typing import Dict, Any
from datetime import datetime

class EarlyCatalystPhase:
    def __init__(self, perplexity_client, fmp_client):
        self.perplexity = perplexity_client
        self.fmp = fmp_client
    
    def analyze(self, news_data: Dict[str, Any], macro_indicators: Dict[str, Any],
               analyst_ratings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze early catalysts from multiple sources.
        
        Args:
            news_data: News and product announcement data
            macro_indicators: Macro economic indicators
            analyst_ratings: Analyst rating changes
            
        Returns:
            Dict containing analysis results
        """
        # Get product launch analysis
        product_analysis = self._analyze_product_launches(news_data)
        
        # Get SEC filing analysis
        sec_analysis = self._analyze_sec_filings(news_data)
        
        # Get insider trading analysis
        insider_analysis = self._get_insider_trading_data()
        
        # Combine analyses
        catalysts = {
            "macro": self._analyze_macro_catalysts(macro_indicators),
            "product": product_analysis,
            "sec": sec_analysis,
            "insider": insider_analysis,
            "analyst": self._analyze_analyst_catalysts(analyst_ratings)
        }
        
        # Calculate overall catalyst strength
        catalyst_strength = self._calculate_catalyst_strength(catalysts)
        
        return {
            "catalysts": catalysts,
            "strength": catalyst_strength,
            "primary_catalyst": self._identify_primary_catalyst(catalysts),
            "sentiment": self._calculate_catalyst_sentiment(catalysts)
        }
    
    def _analyze_product_launches(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze product launches and updates"""
        try:
            # Extract product-related news
            product_news = [item for item in news_data.get('articles', [])
                          if any(keyword in item['title'].lower() 
                                for keyword in ['launch', 'release', 'update', 'announce'])]
            
            if not product_news:
                return {
                    "has_launches": False,
                    "impact_score": 0,
                    "summary": "No recent product launches detected"
                }
            
            # Analyze each product launch
            launch_analyses = []
            for news in product_news:
                prompt = f"""
                Analyze this Oracle product announcement for market impact:
                Title: {news['title']}
                Description: {news.get('description', '')}
                
                Score from 0-100 based on:
                1. Product significance (40%)
                2. Market potential (30%)
                3. Competitive advantage (30%)
                
                Return only the numerical score.
                """
                
                impact_score = int(self.perplexity.complete(prompt))
                launch_analyses.append({
                    "title": news['title'],
                    "impact_score": impact_score,
                    "date": news.get('publishedAt', '')
                })
            
            # Calculate overall impact
            avg_impact = sum(analysis['impact_score'] for analysis in launch_analyses) / len(launch_analyses)
            
            return {
                "has_launches": True,
                "impact_score": avg_impact,
                "launches": launch_analyses,
                "summary": f"Detected {len(launch_analyses)} product launches with average impact score of {avg_impact:.1f}"
            }
            
        except Exception as e:
            logging.error(f"Error analyzing product launches: {str(e)}")
            return {
                "has_launches": False,
                "impact_score": 0,
                "summary": f"Error analyzing product launches: {str(e)}"
            }
    
    def _analyze_sec_filings(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze SEC filings"""
        try:
            # Extract SEC filing news
            sec_news = [item for item in news_data.get('articles', [])
                       if any(keyword in item['title'].lower() 
                             for keyword in ['sec', 'filing', 'form 8-k', 'form 10-k', 'form 10-q'])]
            
            if not sec_news:
                return {
                    "has_filings": False,
                    "impact_score": 0,
                    "summary": "No recent SEC filings detected"
                }
            
            # Analyze each filing
            filing_analyses = []
            for news in sec_news:
                prompt = f"""
                Analyze this Oracle SEC filing for market impact:
                Title: {news['title']}
                Description: {news.get('description', '')}
                
                Score from 0-100 based on:
                1. Materiality (40%)
                2. Market sensitivity (30%)
                3. Timing relevance (30%)
                
                Return only the numerical score.
                """
                
                impact_score = int(self.perplexity.complete(prompt))
                filing_analyses.append({
                    "title": news['title'],
                    "impact_score": impact_score,
                    "date": news.get('publishedAt', ''),
                    "type": self._classify_filing_type(news['title'])
                })
            
            # Calculate overall impact
            avg_impact = sum(analysis['impact_score'] for analysis in filing_analyses) / len(filing_analyses)
            
            return {
                "has_filings": True,
                "impact_score": avg_impact,
                "filings": filing_analyses,
                "summary": f"Detected {len(filing_analyses)} SEC filings with average impact score of {avg_impact:.1f}"
            }
            
        except Exception as e:
            logging.error(f"Error analyzing SEC filings: {str(e)}")
            return {
                "has_filings": False,
                "impact_score": 0,
                "summary": f"Error analyzing SEC filings: {str(e)}"
            }
    
    def _get_insider_trading_data(self) -> Dict[str, Any]:
        """Get and analyze insider trading data"""
        try:
            data = self.fmp.get_insider_trading("ORCL")
            
            if not data:
                return {
                    "has_insider_activity": False,
                    "impact_score": 0,
                    "summary": "No recent insider trading activity"
                }
            
            # Analyze recent insider trades
            recent_trades = data[:5]  # Last 5 trades
            trade_analyses = []
            
            for trade in recent_trades:
                # Calculate trade impact
                transaction_value = float(trade.get('transactionValue', 0))
                transaction_type = trade.get('transactionType', '').lower()
                
                # Score based on transaction value and type
                if transaction_value > 1000000:  # $1M+
                    value_score = 100
                elif transaction_value > 500000:  # $500K+
                    value_score = 75
                elif transaction_value > 100000:  # $100K+
                    value_score = 50
                else:
                    value_score = 25
                
                # Adjust score based on transaction type
                if 'buy' in transaction_type:
                    type_multiplier = 1.2  # Buying is more significant
                elif 'sell' in transaction_type:
                    type_multiplier = 0.8  # Selling is less significant
                else:
                    type_multiplier = 1.0
                
                impact_score = value_score * type_multiplier
                
                trade_analyses.append({
                    "date": trade.get('transactionDate', ''),
                    "type": transaction_type,
                    "value": transaction_value,
                    "impact_score": impact_score,
                    "insider": trade.get('insiderName', '')
                })
            
            # Calculate overall impact
            avg_impact = sum(analysis['impact_score'] for analysis in trade_analyses) / len(trade_analyses)
            
            return {
                "has_insider_activity": True,
                "impact_score": avg_impact,
                "trades": trade_analyses,
                "summary": f"Detected {len(trade_analyses)} insider trades with average impact score of {avg_impact:.1f}"
            }
            
        except Exception as e:
            logging.error(f"Error getting insider trading data: {str(e)}")
            return {
                "has_insider_activity": False,
                "impact_score": 0,
                "summary": f"Error getting insider trading data: {str(e)}"
            }
    
    def _classify_filing_type(self, title: str) -> str:
        """Classify SEC filing type from title"""
        title_lower = title.lower()
        if '8-k' in title_lower:
            return '8-K'
        elif '10-k' in title_lower:
            return '10-K'
        elif '10-q' in title_lower:
            return '10-Q'
        elif 'insider' in title_lower or 'form 4' in title_lower:
            return 'Form 4'
        else:
            return 'Other'
    
    def _calculate_catalyst_strength(self, catalysts: Dict[str, Any]) -> float:
        """Calculate overall catalyst strength (0-100)"""
        weights = {
            "macro": 0.2,
            "product": 0.3,
            "sec": 0.2,
            "insider": 0.15,
            "analyst": 0.15
        }
        
        strength = 0
        for category, weight in weights.items():
            if category in catalysts:
                category_strength = catalysts[category].get("impact_score", 0)
                strength += category_strength * weight
        
        return min(max(strength, 0), 100)
    
    def _identify_primary_catalyst(self, catalysts: Dict[str, Any]) -> str:
        """Identify the strongest individual catalyst"""
        primary_catalyst = None
        max_strength = 0
        
        for category, data in catalysts.items():
            if isinstance(data, dict) and "impact_score" in data:
                if data["impact_score"] > max_strength:
                    max_strength = data["impact_score"]
                    primary_catalyst = f"{category}_{data.get('summary', 'unknown')}"
        
        return primary_catalyst or "No strong catalyst identified" 