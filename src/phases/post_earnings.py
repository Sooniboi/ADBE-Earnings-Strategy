"""
Post-Earnings Phase Module
Handles analysis and trading decisions for the post-earnings phase.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

class PostEarningsPhase:
    def __init__(self, fmp_client, options_client, news_client):
        self.fmp = fmp_client
        self.options = options_client
        self.news = news_client
    
    def analyze(self, earnings_data: Dict[str, Any], market_data: Dict[str, Any],
               news_data: Dict[str, Any], days_since_earnings: int) -> Dict[str, Any]:
        """
        Analyze post-earnings market conditions and sentiment.
        
        Args:
            earnings_data: Earnings report data
            market_data: Market data since earnings
            news_data: News data since earnings
            days_since_earnings: Number of days since earnings
            
        Returns:
            Dict containing analysis results
        """
        # Get price action analysis
        price_analysis = self._analyze_price_action(market_data)
        
        # Get volume analysis
        volume_analysis = self._analyze_volume_patterns(market_data)
        
        # Get options analysis
        options_analysis = self._analyze_options_activity(market_data)
        
        # Get news analysis
        news_analysis = self._analyze_news_sentiment(news_data)
        
        # Combine analyses
        analysis = {
            "price": price_analysis,
            "volume": volume_analysis,
            "options": options_analysis,
            "news": news_analysis,
            "days_since_earnings": days_since_earnings
        }
        
        # Calculate overall sentiment
        sentiment = self._calculate_post_earnings_sentiment(analysis)
        
        return {
            "analysis": analysis,
            "sentiment": sentiment,
            "risk_level": self._calculate_risk_level(analysis),
            "recommended_action": self._get_action_recommendation(analysis)
        }
    
    def _analyze_price_action(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze price action since earnings"""
        try:
            if not market_data:
                return {
                    "has_data": False,
                    "summary": "No market data available"
                }
            
            # Calculate price metrics
            prices = [float(day.get('close', 0)) for day in market_data]
            if not prices:
                return {
                    "has_data": False,
                    "summary": "No price data available"
                }
            
            # Calculate price changes
            initial_price = prices[0]
            current_price = prices[-1]
            total_change_pct = ((current_price - initial_price) / initial_price) * 100
            
            # Calculate daily changes
            daily_changes = []
            for i in range(1, len(prices)):
                daily_change = ((prices[i] - prices[i-1]) / prices[i-1]) * 100
                daily_changes.append(daily_change)
            
            # Calculate volatility
            volatility = self._calculate_volatility(daily_changes)
            
            # Calculate trend
            trend = self._calculate_trend(prices)
            
            return {
                "has_data": True,
                "initial_price": initial_price,
                "current_price": current_price,
                "total_change_pct": total_change_pct,
                "daily_changes": daily_changes,
                "volatility": volatility,
                "trend": trend,
                "summary": f"Price {trend} with {total_change_pct:.1f}% total change and {volatility:.1f}% volatility"
            }
            
        except Exception as e:
            logging.error(f"Error analyzing price action: {str(e)}")
            return {
                "has_data": False,
                "summary": f"Error analyzing price action: {str(e)}"
            }
    
    def _analyze_volume_patterns(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze volume patterns since earnings"""
        try:
            if not market_data:
                return {
                    "has_data": False,
                    "summary": "No market data available"
                }
            
            # Calculate volume metrics
            volumes = [float(day.get('volume', 0)) for day in market_data]
            if not volumes:
                return {
                    "has_data": False,
                    "summary": "No volume data available"
                }
            
            # Calculate average volume
            avg_volume = sum(volumes) / len(volumes)
            
            # Calculate volume trend
            volume_trend = self._calculate_trend(volumes)
            
            # Calculate volume volatility
            volume_volatility = self._calculate_volatility(volumes)
            
            # Calculate volume ratios
            volume_ratios = [vol / avg_volume for vol in volumes]
            
            return {
                "has_data": True,
                "average_volume": avg_volume,
                "volume_trend": volume_trend,
                "volume_volatility": volume_volatility,
                "volume_ratios": volume_ratios,
                "summary": f"Volume {volume_trend} with {volume_volatility:.1f}% volatility"
            }
            
        except Exception as e:
            logging.error(f"Error analyzing volume patterns: {str(e)}")
            return {
                "has_data": False,
                "summary": f"Error analyzing volume patterns: {str(e)}"
            }
    
    def _analyze_options_activity(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze options activity since earnings"""
        try:
            options_data = market_data.get('options', {})
            
            if not options_data:
                return {
                    "has_data": False,
                    "summary": "No options data available"
                }
            
            # Calculate options metrics
            put_volume = float(options_data.get('put_volume', 0))
            call_volume = float(options_data.get('call_volume', 0))
            put_call_ratio = put_volume / call_volume if call_volume != 0 else 0
            
            # Calculate IV changes
            iv_change = float(options_data.get('iv_change', 0))
            
            # Calculate options flow
            options_flow = self._calculate_options_flow(options_data)
            
            return {
                "has_data": True,
                "put_volume": put_volume,
                "call_volume": call_volume,
                "put_call_ratio": put_call_ratio,
                "iv_change": iv_change,
                "options_flow": options_flow,
                "summary": f"Put/call ratio: {put_call_ratio:.2f}, IV change: {iv_change:.1f}%"
            }
            
        except Exception as e:
            logging.error(f"Error analyzing options activity: {str(e)}")
            return {
                "has_data": False,
                "summary": f"Error analyzing options activity: {str(e)}"
            }
    
    def _analyze_news_sentiment(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze news sentiment since earnings"""
        try:
            if not news_data:
                return {
                    "has_data": False,
                    "summary": "No news data available"
                }
            
            # Get recent news articles
            articles = news_data.get('articles', [])
            
            # Analyze each article
            article_analyses = []
            for article in articles:
                # Calculate sentiment score
                sentiment_score = self._calculate_article_sentiment(article)
                
                article_analyses.append({
                    "title": article.get('title', ''),
                    "source": article.get('source', {}).get('name', ''),
                    "published_at": article.get('publishedAt', ''),
                    "sentiment_score": sentiment_score
                })
            
            # Calculate overall sentiment
            if article_analyses:
                avg_sentiment = sum(a['sentiment_score'] for a in article_analyses) / len(article_analyses)
            else:
                avg_sentiment = 0
            
            return {
                "has_data": True,
                "articles": article_analyses,
                "average_sentiment": avg_sentiment,
                "summary": f"Average news sentiment: {avg_sentiment:.1f}"
            }
            
        except Exception as e:
            logging.error(f"Error analyzing news sentiment: {str(e)}")
            return {
                "has_data": False,
                "summary": f"Error analyzing news sentiment: {str(e)}"
            }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values"""
        if len(values) < 2:
            return "neutral"
        
        # Calculate simple linear regression
        x = list(range(len(values)))
        y = values
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(i * j for i, j in zip(x, y))
        sum_xx = sum(i * i for i in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "neutral"
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility (standard deviation) of values"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        squared_diff_sum = sum((x - mean) ** 2 for x in values)
        variance = squared_diff_sum / (len(values) - 1)
        
        return (variance ** 0.5) / mean * 100  # Return as percentage
    
    def _calculate_options_flow(self, options_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate options flow metrics"""
        try:
            # Get options flow data
            flow_data = options_data.get('flow', {})
            
            if not flow_data:
                return {
                    "has_flow": False,
                    "summary": "No options flow data available"
                }
            
            # Calculate flow metrics
            call_flow = float(flow_data.get('call_flow', 0))
            put_flow = float(flow_data.get('put_flow', 0))
            net_flow = call_flow - put_flow
            
            # Calculate flow ratios
            total_flow = call_flow + put_flow
            call_ratio = call_flow / total_flow if total_flow != 0 else 0
            put_ratio = put_flow / total_flow if total_flow != 0 else 0
            
            return {
                "has_flow": True,
                "call_flow": call_flow,
                "put_flow": put_flow,
                "net_flow": net_flow,
                "call_ratio": call_ratio,
                "put_ratio": put_ratio,
                "summary": f"Net options flow: {net_flow:,.0f} (Calls: {call_ratio:.1%}, Puts: {put_ratio:.1%})"
            }
            
        except Exception as e:
            logging.error(f"Error calculating options flow: {str(e)}")
            return {
                "has_flow": False,
                "summary": f"Error calculating options flow: {str(e)}"
            }
    
    def _calculate_article_sentiment(self, article: Dict[str, Any]) -> float:
        """Calculate sentiment score for a news article"""
        try:
            # Extract text for analysis
            title = article.get('title', '')
            description = article.get('description', '')
            content = article.get('content', '')
            
            # Combine text for analysis
            text = f"{title} {description} {content}"
            
            # Calculate sentiment score (-1 to 1)
            # This is a placeholder - in practice, you would use a proper sentiment analysis model
            # For now, we'll use a simple keyword-based approach
            positive_words = ['beat', 'surpass', 'growth', 'positive', 'strong', 'increase']
            negative_words = ['miss', 'decline', 'weak', 'negative', 'decrease', 'concern']
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            total_count = positive_count + negative_count
            if total_count == 0:
                return 0
            
            return (positive_count - negative_count) / total_count
            
        except Exception as e:
            logging.error(f"Error calculating article sentiment: {str(e)}")
            return 0
    
    def _calculate_post_earnings_sentiment(self, analysis: Dict[str, Any]) -> str:
        """Calculate overall post-earnings sentiment"""
        try:
            # Get component sentiments
            price_sentiment = self._get_price_sentiment(analysis['price'])
            volume_sentiment = self._get_volume_sentiment(analysis['volume'])
            options_sentiment = self._get_options_sentiment(analysis['options'])
            news_sentiment = self._get_news_sentiment(analysis['news'])
            
            # Combine sentiments with weights
            weights = {
                "price": 0.3,
                "volume": 0.2,
                "options": 0.3,
                "news": 0.2
            }
            
            sentiment_scores = {
                "bullish": 1,
                "neutral": 0,
                "bearish": -1
            }
            
            weighted_score = (
                sentiment_scores[price_sentiment] * weights["price"] +
                sentiment_scores[volume_sentiment] * weights["volume"] +
                sentiment_scores[options_sentiment] * weights["options"] +
                sentiment_scores[news_sentiment] * weights["news"]
            )
            
            # Determine final sentiment
            if weighted_score > 0.2:
                return "bullish"
            elif weighted_score < -0.2:
                return "bearish"
            else:
                return "neutral"
                
        except Exception as e:
            logging.error(f"Error calculating post-earnings sentiment: {str(e)}")
            return "neutral"
    
    def _get_price_sentiment(self, price_analysis: Dict[str, Any]) -> str:
        """Get sentiment from price analysis"""
        if not price_analysis.get('has_data', False):
            return "neutral"
        
        total_change = price_analysis.get('total_change_pct', 0)
        trend = price_analysis.get('trend', 'neutral')
        
        if total_change > 2 and trend == 'increasing':
            return "bullish"
        elif total_change < -2 and trend == 'decreasing':
            return "bearish"
        else:
            return "neutral"
    
    def _get_volume_sentiment(self, volume_analysis: Dict[str, Any]) -> str:
        """Get sentiment from volume analysis"""
        if not volume_analysis.get('has_data', False):
            return "neutral"
        
        volume_trend = volume_analysis.get('volume_trend', 'neutral')
        
        if volume_trend == 'increasing':
            return "bullish"
        elif volume_trend == 'decreasing':
            return "bearish"
        else:
            return "neutral"
    
    def _get_options_sentiment(self, options_analysis: Dict[str, Any]) -> str:
        """Get sentiment from options analysis"""
        if not options_analysis.get('has_data', False):
            return "neutral"
        
        put_call_ratio = options_analysis.get('put_call_ratio', 1.0)
        options_flow = options_analysis.get('options_flow', {})
        
        if put_call_ratio < 0.8 and options_flow.get('net_flow', 0) > 0:
            return "bullish"
        elif put_call_ratio > 1.2 and options_flow.get('net_flow', 0) < 0:
            return "bearish"
        else:
            return "neutral"
    
    def _get_news_sentiment(self, news_analysis: Dict[str, Any]) -> str:
        """Get sentiment from news analysis"""
        if not news_analysis.get('has_data', False):
            return "neutral"
        
        avg_sentiment = news_analysis.get('average_sentiment', 0)
        
        if avg_sentiment > 0.2:
            return "bullish"
        elif avg_sentiment < -0.2:
            return "bearish"
        else:
            return "neutral"
    
    def _calculate_risk_level(self, analysis: Dict[str, Any]) -> str:
        """Calculate risk level based on analysis"""
        try:
            # Get component risk scores
            price_risk = self._get_price_risk(analysis['price'])
            volume_risk = self._get_volume_risk(analysis['volume'])
            options_risk = self._get_options_risk(analysis['options'])
            news_risk = self._get_news_risk(analysis['news'])
            
            # Combine risks with weights
            weights = {
                "price": 0.3,
                "volume": 0.2,
                "options": 0.3,
                "news": 0.2
            }
            
            weighted_risk = (
                price_risk * weights["price"] +
                volume_risk * weights["volume"] +
                options_risk * weights["options"] +
                news_risk * weights["news"]
            )
            
            # Determine risk level
            if weighted_risk > 0.7:
                return "high"
            elif weighted_risk < 0.3:
                return "low"
            else:
                return "medium"
                
        except Exception as e:
            logging.error(f"Error calculating risk level: {str(e)}")
            return "medium"
    
    def _get_price_risk(self, price_analysis: Dict[str, Any]) -> float:
        """Get risk score from price analysis"""
        if not price_analysis.get('has_data', False):
            return 0.5
        
        # Calculate risk based on volatility and trend strength
        volatility = price_analysis.get('volatility', 0)
        total_change = abs(price_analysis.get('total_change_pct', 0))
        
        volatility_risk = min(volatility / 50, 1.0)  # Normalize to 0-1
        change_risk = min(total_change / 10, 1.0)  # Normalize to 0-1
        
        return (volatility_risk + change_risk) / 2
    
    def _get_volume_risk(self, volume_analysis: Dict[str, Any]) -> float:
        """Get risk score from volume analysis"""
        if not volume_analysis.get('has_data', False):
            return 0.5
        
        # Calculate risk based on volume volatility
        volatility = volume_analysis.get('volume_volatility', 0)
        return min(volatility / 100, 1.0)  # Normalize to 0-1
    
    def _get_options_risk(self, options_analysis: Dict[str, Any]) -> float:
        """Get risk score from options analysis"""
        if not options_analysis.get('has_data', False):
            return 0.5
        
        # Calculate risk based on IV and put/call ratio
        iv_change = abs(options_analysis.get('iv_change', 0))
        put_call_ratio = options_analysis.get('put_call_ratio', 1.0)
        
        iv_risk = min(iv_change / 50, 1.0)  # Normalize to 0-1
        pcr_risk = min(abs(put_call_ratio - 1.0), 1.0)
        
        return (iv_risk + pcr_risk) / 2
    
    def _get_news_risk(self, news_analysis: Dict[str, Any]) -> float:
        """Get risk score from news analysis"""
        if not news_analysis.get('has_data', False):
            return 0.5
        
        # Calculate risk based on sentiment volatility
        articles = news_analysis.get('articles', [])
        if not articles:
            return 0.5
        
        sentiment_scores = [abs(a['sentiment_score']) for a in articles]
        return min(sum(sentiment_scores) / len(sentiment_scores), 1.0)
    
    def _get_action_recommendation(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get action recommendation based on analysis"""
        sentiment = analysis.get('sentiment', 'neutral')
        risk_level = analysis.get('risk_level', 'medium')
        days_since_earnings = analysis.get('days_since_earnings', 0)
        
        # Base position size on risk level
        position_sizes = {
            "high": 0.5,    # 50% of normal size
            "medium": 0.75, # 75% of normal size
            "low": 1.0      # 100% of normal size
        }
        
        # Determine action type
        if sentiment == "bullish":
            action_type = "buy"
        elif sentiment == "bearish":
            action_type = "sell"
        else:
            action_type = "hold"
        
        # Calculate position size
        base_size = position_sizes[risk_level]
        
        # Adjust size based on days since earnings
        if days_since_earnings <= 2:
            base_size *= 0.5  # Reduce size in first 2 days
        
        return {
            "type": action_type,
            "size": base_size,
            "risk_level": risk_level,
            "days_since_earnings": days_since_earnings,
            "summary": f"Recommended {action_type} at {base_size*100:.0f}% of normal size due to {risk_level} risk"
        } 