"""
Pre-Earnings Phase Module
Handles analysis and trading decisions for the pre-earnings phase.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

class PreEarningsPhase:
    def __init__(self, fmp_client, options_client):
        self.fmp = fmp_client
        self.options = options_client
    
    def analyze(self, days_to_earnings: int, historical_data: Dict[str, Any],
               options_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze pre-earnings market conditions and sentiment.
        
        Args:
            days_to_earnings: Number of days until earnings
            historical_data: Historical price and volume data
            options_data: Options chain data
            
        Returns:
            Dict containing analysis results
        """
        # Get historical earnings analysis
        earnings_history = self._analyze_earnings_history(historical_data)
        
        # Get options analysis
        options_analysis = self._analyze_options_chain(options_data)
        
        # Get volume analysis
        volume_analysis = self._analyze_volume_patterns(historical_data)
        
        # Combine analyses
        analysis = {
            "earnings_history": earnings_history,
            "options": options_analysis,
            "volume": volume_analysis,
            "days_to_earnings": days_to_earnings
        }
        
        # Calculate overall sentiment
        sentiment = self._calculate_pre_earnings_sentiment(analysis)
        
        return {
            "analysis": analysis,
            "sentiment": sentiment,
            "risk_level": self._calculate_risk_level(analysis),
            "recommended_position": self._get_position_recommendation(analysis)
        }
    
    def _analyze_earnings_history(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze historical earnings performance"""
        try:
            earnings_data = self.fmp.get_earnings_history("ORCL")
            
            if not earnings_data:
                return {
                    "has_history": False,
                    "summary": "No earnings history available"
                }
            
            # Analyze last 4 quarters
            recent_earnings = earnings_data[:4]
            analyses = []
            
            for earnings in recent_earnings:
                # Calculate surprise metrics
                actual_eps = float(earnings.get('actualEPS', 0))
                expected_eps = float(earnings.get('expectedEPS', 0))
                surprise_pct = ((actual_eps - expected_eps) / abs(expected_eps)) * 100 if expected_eps != 0 else 0
                
                # Calculate revenue metrics
                actual_revenue = float(earnings.get('actualRevenue', 0))
                expected_revenue = float(earnings.get('expectedRevenue', 0))
                revenue_surprise_pct = ((actual_revenue - expected_revenue) / abs(expected_revenue)) * 100 if expected_revenue != 0 else 0
                
                analyses.append({
                    "date": earnings.get('date', ''),
                    "actual_eps": actual_eps,
                    "expected_eps": expected_eps,
                    "surprise_pct": surprise_pct,
                    "actual_revenue": actual_revenue,
                    "expected_revenue": expected_revenue,
                    "revenue_surprise_pct": revenue_surprise_pct,
                    "period": earnings.get('period', '')
                })
            
            # Calculate trends
            eps_trend = self._calculate_trend([a['surprise_pct'] for a in analyses])
            revenue_trend = self._calculate_trend([a['revenue_surprise_pct'] for a in analyses])
            
            return {
                "has_history": True,
                "analyses": analyses,
                "eps_trend": eps_trend,
                "revenue_trend": revenue_trend,
                "summary": f"Last 4 quarters show {eps_trend} EPS surprises and {revenue_trend} revenue surprises"
            }
            
        except Exception as e:
            logging.error(f"Error analyzing earnings history: {str(e)}")
            return {
                "has_history": False,
                "summary": f"Error analyzing earnings history: {str(e)}"
            }
    
    def _analyze_options_chain(self, options_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze options chain for earnings expectations"""
        try:
            if not options_data:
                return {
                    "has_options_data": False,
                    "summary": "No options data available"
                }
            
            # Calculate implied volatility skew
            iv_skew = self._calculate_iv_skew(options_data)
            
            # Calculate put/call ratio
            put_call_ratio = self._calculate_put_call_ratio(options_data)
            
            # Analyze options volume
            volume_analysis = self._analyze_options_volume(options_data)
            
            return {
                "has_options_data": True,
                "iv_skew": iv_skew,
                "put_call_ratio": put_call_ratio,
                "volume_analysis": volume_analysis,
                "summary": f"Options data shows {iv_skew} IV skew and {put_call_ratio:.2f} put/call ratio"
            }
            
        except Exception as e:
            logging.error(f"Error analyzing options chain: {str(e)}")
            return {
                "has_options_data": False,
                "summary": f"Error analyzing options chain: {str(e)}"
            }
    
    def _analyze_volume_patterns(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trading volume patterns"""
        try:
            if not historical_data:
                return {
                    "has_volume_data": False,
                    "summary": "No volume data available"
                }
            
            # Calculate average volume
            volumes = [float(day.get('volume', 0)) for day in historical_data]
            avg_volume = sum(volumes) / len(volumes)
            
            # Calculate volume trend
            recent_volumes = volumes[-5:]  # Last 5 days
            volume_trend = self._calculate_trend(recent_volumes)
            
            # Calculate volume volatility
            volume_volatility = self._calculate_volatility(volumes)
            
            return {
                "has_volume_data": True,
                "average_volume": avg_volume,
                "volume_trend": volume_trend,
                "volume_volatility": volume_volatility,
                "summary": f"Volume shows {volume_trend} trend with {volume_volatility:.1f}% volatility"
            }
            
        except Exception as e:
            logging.error(f"Error analyzing volume patterns: {str(e)}")
            return {
                "has_volume_data": False,
                "summary": f"Error analyzing volume patterns: {str(e)}"
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
    
    def _calculate_iv_skew(self, options_data: Dict[str, Any]) -> str:
        """Calculate implied volatility skew"""
        try:
            # Get ATM and OTM options
            atm_options = [opt for opt in options_data if abs(float(opt.get('strike', 0)) - float(options_data[0].get('underlying_price', 0))) < 5]
            otm_puts = [opt for opt in options_data if float(opt.get('strike', 0)) < float(options_data[0].get('underlying_price', 0))]
            
            if not atm_options or not otm_puts:
                return "neutral"
            
            # Calculate average IV
            atm_iv = sum(float(opt.get('implied_volatility', 0)) for opt in atm_options) / len(atm_options)
            otm_put_iv = sum(float(opt.get('implied_volatility', 0)) for opt in otm_puts) / len(otm_puts)
            
            # Determine skew
            if otm_put_iv > atm_iv * 1.2:
                return "high"
            elif otm_put_iv < atm_iv * 0.8:
                return "low"
            else:
                return "neutral"
                
        except Exception as e:
            logging.error(f"Error calculating IV skew: {str(e)}")
            return "neutral"
    
    def _calculate_put_call_ratio(self, options_data: Dict[str, Any]) -> float:
        """Calculate put/call ratio"""
        try:
            puts = [opt for opt in options_data if opt.get('option_type', '').lower() == 'put']
            calls = [opt for opt in options_data if opt.get('option_type', '').lower() == 'call']
            
            put_volume = sum(float(opt.get('volume', 0)) for opt in puts)
            call_volume = sum(float(opt.get('volume', 0)) for opt in calls)
            
            return put_volume / call_volume if call_volume > 0 else 0
            
        except Exception as e:
            logging.error(f"Error calculating put/call ratio: {str(e)}")
            return 0.0
    
    def _analyze_options_volume(self, options_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze options volume patterns"""
        try:
            # Group by expiration
            expirations = {}
            for opt in options_data:
                exp = opt.get('expiration_date', '')
                if exp not in expirations:
                    expirations[exp] = []
                expirations[exp].append(opt)
            
            # Analyze each expiration
            analyses = []
            for exp, options in expirations.items():
                total_volume = sum(float(opt.get('volume', 0)) for opt in options)
                put_volume = sum(float(opt.get('volume', 0)) for opt in options if opt.get('option_type', '').lower() == 'put')
                call_volume = sum(float(opt.get('volume', 0)) for opt in options if opt.get('option_type', '').lower() == 'call')
                
                analyses.append({
                    "expiration": exp,
                    "total_volume": total_volume,
                    "put_volume": put_volume,
                    "call_volume": call_volume,
                    "put_call_ratio": put_volume / call_volume if call_volume > 0 else 0
                })
            
            return {
                "expiration_analyses": analyses,
                "summary": f"Analyzed volume across {len(analyses)} expiration dates"
            }
            
        except Exception as e:
            logging.error(f"Error analyzing options volume: {str(e)}")
            return {
                "summary": f"Error analyzing options volume: {str(e)}"
            }
    
    def _calculate_pre_earnings_sentiment(self, analysis: Dict[str, Any]) -> str:
        """Calculate overall pre-earnings sentiment"""
        try:
            # Get component sentiments
            earnings_sentiment = self._get_earnings_sentiment(analysis['earnings_history'])
            options_sentiment = self._get_options_sentiment(analysis['options'])
            volume_sentiment = self._get_volume_sentiment(analysis['volume'])
            
            # Combine sentiments with weights
            weights = {
                "earnings": 0.4,
                "options": 0.4,
                "volume": 0.2
            }
            
            sentiment_scores = {
                "bullish": 1,
                "neutral": 0,
                "bearish": -1
            }
            
            weighted_score = (
                sentiment_scores[earnings_sentiment] * weights["earnings"] +
                sentiment_scores[options_sentiment] * weights["options"] +
                sentiment_scores[volume_sentiment] * weights["volume"]
            )
            
            # Determine final sentiment
            if weighted_score > 0.2:
                return "bullish"
            elif weighted_score < -0.2:
                return "bearish"
            else:
                return "neutral"
                
        except Exception as e:
            logging.error(f"Error calculating pre-earnings sentiment: {str(e)}")
            return "neutral"
    
    def _get_earnings_sentiment(self, earnings_analysis: Dict[str, Any]) -> str:
        """Get sentiment from earnings analysis"""
        if not earnings_analysis.get('has_history', False):
            return "neutral"
        
        eps_trend = earnings_analysis.get('eps_trend', 'neutral')
        revenue_trend = earnings_analysis.get('revenue_trend', 'neutral')
        
        if eps_trend == 'increasing' and revenue_trend == 'increasing':
            return "bullish"
        elif eps_trend == 'decreasing' and revenue_trend == 'decreasing':
            return "bearish"
        else:
            return "neutral"
    
    def _get_options_sentiment(self, options_analysis: Dict[str, Any]) -> str:
        """Get sentiment from options analysis"""
        if not options_analysis.get('has_options_data', False):
            return "neutral"
        
        iv_skew = options_analysis.get('iv_skew', 'neutral')
        put_call_ratio = options_analysis.get('put_call_ratio', 1.0)
        
        if iv_skew == 'high' and put_call_ratio > 1.2:
            return "bearish"
        elif iv_skew == 'low' and put_call_ratio < 0.8:
            return "bullish"
        else:
            return "neutral"
    
    def _get_volume_sentiment(self, volume_analysis: Dict[str, Any]) -> str:
        """Get sentiment from volume analysis"""
        if not volume_analysis.get('has_volume_data', False):
            return "neutral"
        
        volume_trend = volume_analysis.get('volume_trend', 'neutral')
        
        if volume_trend == 'increasing':
            return "bullish"
        elif volume_trend == 'decreasing':
            return "bearish"
        else:
            return "neutral"
    
    def _calculate_risk_level(self, analysis: Dict[str, Any]) -> str:
        """Calculate risk level based on analysis"""
        try:
            # Get component risk scores
            earnings_risk = self._get_earnings_risk(analysis['earnings_history'])
            options_risk = self._get_options_risk(analysis['options'])
            volume_risk = self._get_volume_risk(analysis['volume'])
            
            # Combine risks with weights
            weights = {
                "earnings": 0.4,
                "options": 0.4,
                "volume": 0.2
            }
            
            weighted_risk = (
                earnings_risk * weights["earnings"] +
                options_risk * weights["options"] +
                volume_risk * weights["volume"]
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
        if not earnings_analysis.get('has_history', False):
            return 0.5
        
        # Calculate risk based on earnings surprise volatility
        surprises = [abs(a['surprise_pct']) for a in earnings_analysis.get('analyses', [])]
        if not surprises:
            return 0.5
        
        avg_surprise = sum(surprises) / len(surprises)
        return min(avg_surprise / 100, 1.0)  # Normalize to 0-1
    
    def _get_options_risk(self, options_analysis: Dict[str, Any]) -> float:
        """Get risk score from options analysis"""
        if not options_analysis.get('has_options_data', False):
            return 0.5
        
        # Calculate risk based on IV and put/call ratio
        iv_skew = options_analysis.get('iv_skew', 'neutral')
        put_call_ratio = options_analysis.get('put_call_ratio', 1.0)
        
        iv_score = 0.5
        if iv_skew == 'high':
            iv_score = 0.8
        elif iv_skew == 'low':
            iv_score = 0.2
        
        pcr_score = min(abs(put_call_ratio - 1.0), 1.0)
        
        return (iv_score + pcr_score) / 2
    
    def _get_volume_risk(self, volume_analysis: Dict[str, Any]) -> float:
        """Get risk score from volume analysis"""
        if not volume_analysis.get('has_volume_data', False):
            return 0.5
        
        # Calculate risk based on volume volatility
        volatility = volume_analysis.get('volume_volatility', 0)
        return min(volatility / 100, 1.0)  # Normalize to 0-1
    
    def _get_position_recommendation(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get position recommendation based on analysis"""
        sentiment = analysis.get('sentiment', 'neutral')
        risk_level = analysis.get('risk_level', 'medium')
        days_to_earnings = analysis.get('days_to_earnings', 0)
        
        # Base position size on risk level
        position_sizes = {
            "high": 0.5,    # 50% of normal size
            "medium": 0.75, # 75% of normal size
            "low": 1.0      # 100% of normal size
        }
        
        # Determine position type
        if sentiment == "bullish":
            position_type = "long"
        elif sentiment == "bearish":
            position_type = "short"
        else:
            position_type = "neutral"
        
        # Calculate position size
        base_size = position_sizes[risk_level]
        if days_to_earnings <= 2:
            base_size *= 0.5  # Reduce size in last 2 days
        
        return {
            "type": position_type,
            "size": base_size,
            "risk_level": risk_level,
            "days_to_earnings": days_to_earnings,
            "summary": f"Recommended {position_type} position at {base_size*100:.0f}% of normal size due to {risk_level} risk"
        } 