"""
Earnings Day Phase Module
Handles analysis and trading decisions for the earnings day phase.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

class EarningsDayPhase:
    def __init__(self, fmp_client, options_client, news_client):
        self.fmp = fmp_client
        self.options = options_client
        self.news = news_client
    
    def analyze(self, earnings_data: Dict[str, Any], market_data: Dict[str, Any],
               news_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze earnings day market conditions and sentiment.
        
        Args:
            earnings_data: Earnings report data
            market_data: Real-time market data
            news_data: Real-time news data
            
        Returns:
            Dict containing analysis results
        """
        # Get earnings analysis
        earnings_analysis = self._analyze_earnings_report(earnings_data)
        
        # Get market reaction analysis
        market_analysis = self._analyze_market_reaction(market_data)
        
        # Get news sentiment analysis
        news_analysis = self._analyze_news_sentiment(news_data)
        
        # Combine analyses
        analysis = {
            "earnings": earnings_analysis,
            "market": market_analysis,
            "news": news_analysis
        }
        
        # Calculate overall sentiment
        sentiment = self._calculate_earnings_day_sentiment(analysis)
        
        return {
            "analysis": analysis,
            "sentiment": sentiment,
            "risk_level": self._calculate_risk_level(analysis),
            "recommended_action": self._get_action_recommendation(analysis)
        }
    
    def _analyze_earnings_report(self, earnings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze earnings report data"""
        try:
            if not earnings_data:
                return {
                    "has_data": False,
                    "summary": "No earnings data available"
                }
            
            # Calculate key metrics
            actual_eps = float(earnings_data.get('actualEPS', 0))
            expected_eps = float(earnings_data.get('expectedEPS', 0))
            eps_surprise = ((actual_eps - expected_eps) / abs(expected_eps)) * 100 if expected_eps != 0 else 0
            
            actual_revenue = float(earnings_data.get('actualRevenue', 0))
            expected_revenue = float(earnings_data.get('expectedRevenue', 0))
            revenue_surprise = ((actual_revenue - expected_revenue) / abs(expected_revenue)) * 100 if expected_revenue != 0 else 0
            
            # Analyze guidance
            guidance_analysis = self._analyze_guidance(earnings_data)
            
            # Analyze segment performance
            segment_analysis = self._analyze_segments(earnings_data)
            
            return {
                "has_data": True,
                "eps": {
                    "actual": actual_eps,
                    "expected": expected_eps,
                    "surprise_pct": eps_surprise
                },
                "revenue": {
                    "actual": actual_revenue,
                    "expected": expected_revenue,
                    "surprise_pct": revenue_surprise
                },
                "guidance": guidance_analysis,
                "segments": segment_analysis,
                "summary": f"EPS surprise: {eps_surprise:.1f}%, Revenue surprise: {revenue_surprise:.1f}%"
            }
            
        except Exception as e:
            logging.error(f"Error analyzing earnings report: {str(e)}")
            return {
                "has_data": False,
                "summary": f"Error analyzing earnings report: {str(e)}"
            }
    
    def _analyze_market_reaction(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market reaction to earnings"""
        try:
            if not market_data:
                return {
                    "has_data": False,
                    "summary": "No market data available"
                }
            
            # Calculate price movement
            pre_price = float(market_data.get('pre_market_price', 0))
            post_price = float(market_data.get('post_market_price', 0))
            price_change_pct = ((post_price - pre_price) / pre_price) * 100 if pre_price != 0 else 0
            
            # Calculate volume analysis
            volume_analysis = self._analyze_volume(market_data)
            
            # Calculate options analysis
            options_analysis = self._analyze_options_activity(market_data)
            
            return {
                "has_data": True,
                "price_change": {
                    "pre_market": pre_price,
                    "post_market": post_price,
                    "change_pct": price_change_pct
                },
                "volume": volume_analysis,
                "options": options_analysis,
                "summary": f"Post-market price change: {price_change_pct:.1f}%"
            }
            
        except Exception as e:
            logging.error(f"Error analyzing market reaction: {str(e)}")
            return {
                "has_data": False,
                "summary": f"Error analyzing market reaction: {str(e)}"
            }
    
    def _analyze_news_sentiment(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze news sentiment"""
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
    
    def _analyze_guidance(self, earnings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze earnings guidance"""
        try:
            guidance = earnings_data.get('guidance', {})
            
            if not guidance:
                return {
                    "has_guidance": False,
                    "summary": "No guidance provided"
                }
            
            # Analyze EPS guidance
            eps_guidance = guidance.get('eps', {})
            eps_analysis = {
                "has_guidance": bool(eps_guidance),
                "range": {
                    "low": float(eps_guidance.get('low', 0)),
                    "high": float(eps_guidance.get('high', 0))
                } if eps_guidance else None
            }
            
            # Analyze revenue guidance
            revenue_guidance = guidance.get('revenue', {})
            revenue_analysis = {
                "has_guidance": bool(revenue_guidance),
                "range": {
                    "low": float(revenue_guidance.get('low', 0)),
                    "high": float(revenue_guidance.get('high', 0))
                } if revenue_guidance else None
            }
            
            return {
                "has_guidance": True,
                "eps": eps_analysis,
                "revenue": revenue_analysis,
                "summary": "Guidance analysis completed"
            }
            
        except Exception as e:
            logging.error(f"Error analyzing guidance: {str(e)}")
            return {
                "has_guidance": False,
                "summary": f"Error analyzing guidance: {str(e)}"
            }
    
    def _analyze_segments(self, earnings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze segment performance"""
        try:
            segments = earnings_data.get('segments', {})
            
            if not segments:
                return {
                    "has_segments": False,
                    "summary": "No segment data available"
                }
            
            # Analyze each segment
            segment_analyses = []
            for segment_name, segment_data in segments.items():
                # Calculate growth metrics
                revenue = float(segment_data.get('revenue', 0))
                revenue_growth = float(segment_data.get('revenueGrowth', 0))
                margin = float(segment_data.get('margin', 0))
                
                segment_analyses.append({
                    "name": segment_name,
                    "revenue": revenue,
                    "revenue_growth": revenue_growth,
                    "margin": margin
                })
            
            return {
                "has_segments": True,
                "segments": segment_analyses,
                "summary": f"Analyzed {len(segment_analyses)} segments"
            }
            
        except Exception as e:
            logging.error(f"Error analyzing segments: {str(e)}")
            return {
                "has_segments": False,
                "summary": f"Error analyzing segments: {str(e)}"
            }
    
    def _analyze_volume(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trading volume"""
        try:
            volume_data = market_data.get('volume', {})
            
            if not volume_data:
                return {
                    "has_volume": False,
                    "summary": "No volume data available"
                }
            
            # Calculate volume metrics
            pre_market_volume = float(volume_data.get('pre_market', 0))
            post_market_volume = float(volume_data.get('post_market', 0))
            avg_volume = float(volume_data.get('average', 0))
            
            # Calculate volume ratios
            pre_market_ratio = pre_market_volume / avg_volume if avg_volume != 0 else 0
            post_market_ratio = post_market_volume / avg_volume if avg_volume != 0 else 0
            
            return {
                "has_volume": True,
                "pre_market": {
                    "volume": pre_market_volume,
                    "ratio": pre_market_ratio
                },
                "post_market": {
                    "volume": post_market_volume,
                    "ratio": post_market_ratio
                },
                "average": avg_volume,
                "summary": f"Post-market volume is {post_market_ratio:.1f}x average volume"
            }
            
        except Exception as e:
            logging.error(f"Error analyzing volume: {str(e)}")
            return {
                "has_volume": False,
                "summary": f"Error analyzing volume: {str(e)}"
            }
    
    def _analyze_options_activity(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze options activity"""
        try:
            options_data = market_data.get('options', {})
            
            if not options_data:
                return {
                    "has_options": False,
                    "summary": "No options data available"
                }
            
            # Calculate options metrics
            put_volume = float(options_data.get('put_volume', 0))
            call_volume = float(options_data.get('call_volume', 0))
            put_call_ratio = put_volume / call_volume if call_volume != 0 else 0
            
            # Calculate IV changes
            iv_change = float(options_data.get('iv_change', 0))
            
            return {
                "has_options": True,
                "put_volume": put_volume,
                "call_volume": call_volume,
                "put_call_ratio": put_call_ratio,
                "iv_change": iv_change,
                "summary": f"Put/call ratio: {put_call_ratio:.2f}, IV change: {iv_change:.1f}%"
            }
            
        except Exception as e:
            logging.error(f"Error analyzing options activity: {str(e)}")
            return {
                "has_options": False,
                "summary": f"Error analyzing options activity: {str(e)}"
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
    
    def _calculate_earnings_day_sentiment(self, analysis: Dict[str, Any]) -> str:
        """Calculate overall earnings day sentiment"""
        try:
            # Get component sentiments
            earnings_sentiment = self._get_earnings_sentiment(analysis['earnings'])
            market_sentiment = self._get_market_sentiment(analysis['market'])
            news_sentiment = self._get_news_sentiment(analysis['news'])
            
            # Combine sentiments with weights
            weights = {
                "earnings": 0.4,
                "market": 0.4,
                "news": 0.2
            }
            
            sentiment_scores = {
                "bullish": 1,
                "neutral": 0,
                "bearish": -1
            }
            
            weighted_score = (
                sentiment_scores[earnings_sentiment] * weights["earnings"] +
                sentiment_scores[market_sentiment] * weights["market"] +
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
            logging.error(f"Error calculating earnings day sentiment: {str(e)}")
            return "neutral"
    
    def _get_earnings_sentiment(self, earnings_analysis: Dict[str, Any]) -> str:
        """Get sentiment from earnings analysis"""
        if not earnings_analysis.get('has_data', False):
            return "neutral"
        
        eps_surprise = earnings_analysis.get('eps', {}).get('surprise_pct', 0)
        revenue_surprise = earnings_analysis.get('revenue', {}).get('surprise_pct', 0)
        
        if eps_surprise > 5 and revenue_surprise > 5:
            return "bullish"
        elif eps_surprise < -5 and revenue_surprise < -5:
            return "bearish"
        else:
            return "neutral"
    
    def _get_market_sentiment(self, market_analysis: Dict[str, Any]) -> str:
        """Get sentiment from market analysis"""
        if not market_analysis.get('has_data', False):
            return "neutral"
        
        price_change = market_analysis.get('price_change', {}).get('change_pct', 0)
        
        if price_change > 2:
            return "bullish"
        elif price_change < -2:
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
            earnings_risk = self._get_earnings_risk(analysis['earnings'])
            market_risk = self._get_market_risk(analysis['market'])
            news_risk = self._get_news_risk(analysis['news'])
            
            # Combine risks with weights
            weights = {
                "earnings": 0.4,
                "market": 0.4,
                "news": 0.2
            }
            
            weighted_risk = (
                earnings_risk * weights["earnings"] +
                market_risk * weights["market"] +
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
    
    def _get_earnings_risk(self, earnings_analysis: Dict[str, Any]) -> float:
        """Get risk score from earnings analysis"""
        if not earnings_analysis.get('has_data', False):
            return 0.5
        
        # Calculate risk based on surprise magnitude
        eps_surprise = abs(earnings_analysis.get('eps', {}).get('surprise_pct', 0))
        revenue_surprise = abs(earnings_analysis.get('revenue', {}).get('surprise_pct', 0))
        
        return min(max(eps_surprise, revenue_surprise) / 20, 1.0)  # Normalize to 0-1
    
    def _get_market_risk(self, market_analysis: Dict[str, Any]) -> float:
        """Get risk score from market analysis"""
        if not market_analysis.get('has_data', False):
            return 0.5
        
        # Calculate risk based on price movement and volume
        price_change = abs(market_analysis.get('price_change', {}).get('change_pct', 0))
        volume_ratio = market_analysis.get('volume', {}).get('post_market', {}).get('ratio', 1.0)
        
        price_risk = min(price_change / 10, 1.0)  # Normalize to 0-1
        volume_risk = min(volume_ratio / 3, 1.0)  # Normalize to 0-1
        
        return (price_risk + volume_risk) / 2
    
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
        
        return {
            "type": action_type,
            "size": base_size,
            "risk_level": risk_level,
            "summary": f"Recommended {action_type} at {base_size*100:.0f}% of normal size due to {risk_level} risk"
        } 