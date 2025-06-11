"""
Adobe Analyzer Module
Handles market analysis and signal generation for Adobe earnings strategy.
"""

import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
import numpy as np
from scipy import stats

from src.phase_controller import PhaseController
from src.phases.early_catalyst import EarlyCatalystPhase
from src.phases.pre_earnings import PreEarningsPhase
from src.phases.earnings_day import EarningsDayPhase
from src.phases.post_earnings import PostEarningsPhase
from src.data_client import DataClient

load_dotenv()

class AdobeAnalyzer:
    def __init__(self, monitor):
        self.monitor = monitor
        self.phase_controller = PhaseController()
        self.data_client = DataClient()
        self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
        self.alpha_vantage_api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.perplexity_base_url = "https://api.perplexity.ai/chat/completions"
        
        # Initialize phase handlers with data client
        self.phase_handlers = {
            "early_catalyst": EarlyCatalystPhase(self.data_client, None),
            "momentum_volatility": PreEarningsPhase(self.data_client, None),
            "final_pre_earnings": PreEarningsPhase(self.data_client, None),
            "post_earnings": PostEarningsPhase(self.data_client, None, None),
            "no_setup": None
        }
        
        # ADBE-specific parameters
        self.volatility_thresholds = {
            'low': 0.15,    # 15% IV
            'medium': 0.25, # 25% IV
            'high': 0.35    # 35% IV
        }
        
        self.earnings_metrics = {
            'avg_move': 0.072,  # 7.2% average earnings move
            'target_capture': 0.65,  # Target 65% capture
            'max_drawdown': 0.12,  # 12% max drawdown
            'min_sharpe': 1.8  # Minimum Sharpe ratio
        }
        
        # Phase-specific parameters
        self.phase_parameters = {
            'early_catalyst': {
                'min_confidence': 0.60,
                'max_position': 0.10,
                'target_capture': 0.20
            },
            'momentum_volatility': {
                'min_confidence': 0.65,
                'max_position': 0.15,
                'target_capture': 0.30
            },
            'final_pre_earnings': {
                'min_confidence': 0.70,
                'max_position': 0.20,
                'target_capture': 0.40
            },
            'earnings_day': {
                'min_confidence': 0.75,
                'max_position': 0.25,
                'target_capture': 0.50
            },
            'post_earnings': {
                'min_confidence': 0.60,
                'max_position': 0.15,
                'target_capture': 0.30
            }
        }
        
        # Analysis parameters
        self.confidence_threshold = 0.60
        self.min_volume = 1000
        self.min_open_interest = 500
        
        # Technical indicators
        self.rsi_period = 14
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        
        # Volatility parameters
        self.vol_lookback = 20
        self.vol_threshold = 0.25
        
        # Sentiment parameters
        self.sentiment_threshold = 0.5
        self.news_lookback = 7  # days
        
        logging.info("Initialized Adobe Analyzer")
    
    def analyze_oracle(self) -> Dict[str, Any]:
        """Main analysis method for Oracle earnings strategy"""
        try:
            # Log system metrics
            self.monitor.log_system_metrics()
            
            # Get current date and calculate days to earnings
            current_date = datetime.now()
            days_to_earnings = self._calculate_days_to_earnings(current_date)
            
            # Determine current phase
            current_phase = self.phase_controller.determine_phase(days_to_earnings)
            logging.info(f"Current phase: {current_phase}")
            
            # Get phase-specific risk parameters
            risk_params = self.phase_controller.get_phase_risk_params(current_phase)
            
            # Run phase-specific analysis
            if current_phase != "no_setup":
                phase_handler = self.phase_handlers[current_phase]
                analysis_result = self._run_phase_analysis(phase_handler, current_phase, days_to_earnings)
            else:
                analysis_result = {
                    "phase": "no_setup",
                    "message": "No active setup at this time",
                    "days_to_earnings": days_to_earnings
                }
            
            # Enhance analysis with Perplexity
            enhanced_analysis = self._enhance_with_perplexity(analysis_result, current_phase)
            
            # Prepare final result
            result = {
                "timestamp": current_date.isoformat(),
                "phase": current_phase,
                "days_to_earnings": days_to_earnings,
                "risk_parameters": risk_params,
                "analysis": enhanced_analysis
            }
            
            # Log run metrics
            self.monitor.log_run_metrics(
                start_time=current_date,
                end_time=datetime.now(),
                success=True
            )
            
            return result
            
        except Exception as e:
            logging.error(f"Error in analyze_oracle: {str(e)}")
            self.monitor.log_run_metrics(
                start_time=current_date,
                end_time=datetime.now(),
                success=False
            )
            return {
                "error": str(e),
                "phase": current_phase if 'current_phase' in locals() else "unknown",
                "timestamp": current_date.isoformat()
            }
    
    def _calculate_days_to_earnings(self, current_date: datetime) -> int:
        """Calculate days until next earnings"""
        try:
            earnings_history = self.data_client.get_earnings_history()
            if not earnings_history["has_history"]:
                return 5  # Default fallback
            
            # Get the next earnings date
            earnings_dates = [
                datetime.strptime(earning['date'], '%Y-%m-%d')
                for earning in earnings_history["earnings"]
            ]
            earnings_dates.sort()
            
            # Find the next earnings date
            for date in earnings_dates:
                if date > current_date:
                    return (date - current_date).days
            
            return 5  # Default fallback if no future earnings found
            
        except Exception as e:
            logging.error(f"Error calculating days to earnings: {str(e)}")
            return 5  # Default fallback
    
    def _run_phase_analysis(self, phase_handler, phase: str, days_to_earnings: int) -> Dict[str, Any]:
        """Run analysis for a specific phase"""
        try:
            # Get required data for the phase
            data = self._get_phase_data(phase)
            
            # Run phase-specific analysis
            if phase in ["early_catalyst", "momentum_volatility", "final_pre_earnings"]:
                result = phase_handler.analyze(
                    days_to_earnings=days_to_earnings,
                    historical_data=data.get("historical", {}),
                    options_data=data.get("options", {})
                )
            elif phase == "post_earnings":
                result = phase_handler.analyze(
                    earnings_data=data.get("earnings", {}),
                    market_data=data.get("market", {}),
                    news_data=data.get("news", {}),
                    days_since_earnings=abs(days_to_earnings)
                )
            else:
                result = {"error": f"Unknown phase: {phase}"}
            
            return result
            
        except Exception as e:
            logging.error(f"Error in phase analysis: {str(e)}")
            return {"error": str(e)}
    
    def _get_phase_data(self, phase: str) -> Dict[str, Any]:
        """Get required data for a specific phase"""
        try:
            data = {
                "historical": self.data_client.get_volume_data(),
                "options": self.data_client.get_options_data(),
                "earnings": self.data_client.get_earnings_history(),
                "market": self.data_client.get_market_data(),
                "news": self.data_client.get_news_data()
            }
            return data
        except Exception as e:
            logging.error(f"Error getting phase data: {str(e)}")
            return {
                "historical": {},
                "options": {},
                "earnings": {},
                "market": {},
                "news": {}
            }
    
    def _enhance_with_perplexity(self, analysis: Dict[str, Any], phase: str) -> Dict[str, Any]:
        """Enhance analysis with Perplexity AI insights"""
        try:
            # Prepare context for Perplexity
            context = {
                'phase': phase,
                'current_analysis': analysis,
                'market_data': self.monitor.get_market_data(),
                'news_sentiment': self.monitor.get_news_sentiment(),
                'options_data': self.monitor.get_options_data()
            }
            
            # Create prompt for Perplexity
            prompt = self._create_perplexity_prompt(context)
            
            # Call Perplexity API
            response = self._call_perplexity_api(prompt)
            
            # Process Perplexity response
            enhanced_analysis = self._process_perplexity_response(response, analysis)
            
            return enhanced_analysis
            
        except Exception as e:
            logging.error(f"Error enhancing analysis with Perplexity: {str(e)}")
            return analysis
    
    def _create_perplexity_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for Perplexity API"""
        return f"""
        You are analyzing an Adobe (ADBE) earnings trading strategy implementation. Here's the current status and context:

        IMPLEMENTATION STATUS:
        - Phase-based trading system with 5 distinct phases
        - Real-time data integration with IBKR Gateway (port 7497)
        - Paper trading mode enabled for testing
        - Risk management system with circuit breakers
        - Perplexity AI integration for enhanced analysis

        CURRENT PHASE: {context['phase']}

        SYSTEM COMPONENTS:
        1. Data Pipeline (OracleDataBus):
           - Real-time options data (5-min updates)
           - News sentiment analysis (15-min updates)
           - Fundamental data (hourly updates)
           - Macroeconomic indicators (4-hour updates)

        2. Risk Management (OracleRiskEngine):
           - Kelly Criterion position sizing
           - Portfolio VaR calculations
           - Circuit breakers:
             * Max daily loss: 5%
             * Max position size: 10%
             * Max correlation: 70%
             * Min confidence: 60%

        3. Trading Bot (OracleTradingBot):
           - Automated trade execution
           - Position management
           - Real-time monitoring
           - Paper trading mode

        CURRENT MARKET DATA:
        - Price: {context['market_data'].get('price')}
        - Volume: {context['market_data'].get('volume')}
        - IV Rank: {context['market_data'].get('iv_rank')}

        NEWS SENTIMENT:
        - Overall: {context['news_sentiment'].get('overall')}
        - Recent Headlines: {context['news_sentiment'].get('recent_headlines')}

        OPTIONS DATA:
        - Call/Put Ratio: {context['options_data'].get('call_put_ratio')}
        - Volume Profile: {context['options_data'].get('volume_profile')}

        CURRENT ANALYSIS:
        {context['current_analysis']}

        Please provide:
        1. Enhanced market analysis considering our implementation status
        2. Risk assessment based on current phase and system state
        3. Trade recommendations aligned with our risk parameters
        4. Confidence level with justification
        5. Key factors to monitor in current phase
        6. Any potential improvements or adjustments to our current implementation

        Focus on:
        - Phase-specific opportunities
        - Risk management considerations
        - System optimization suggestions
        - Market condition alignment
        - Implementation improvements
        """
    
    def _call_perplexity_api(self, prompt: str) -> Dict[str, Any]:
        """Call Perplexity API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.perplexity_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'pplx-7b-online',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 1000
            }
            
            response = requests.post(
                self.perplexity_base_url,
                headers=headers,
                json=data
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logging.error(f"Error calling Perplexity API: {str(e)}")
            return {}
    
    def _process_perplexity_response(self, response: Dict[str, Any], original_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Process Perplexity API response"""
        try:
            if not response:
                return original_analysis
            
            # Extract Perplexity insights
            perplexity_insights = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Enhance original analysis
            enhanced_analysis = original_analysis.copy()
            enhanced_analysis['perplexity_insights'] = perplexity_insights
            
            # Update confidence based on Perplexity analysis
            if 'confidence' in enhanced_analysis:
                # Adjust confidence based on Perplexity insights
                confidence_adjustment = self._calculate_confidence_adjustment(perplexity_insights)
                enhanced_analysis['confidence'] = min(1.0, enhanced_analysis['confidence'] + confidence_adjustment)
            
            return enhanced_analysis
            
        except Exception as e:
            logging.error(f"Error processing Perplexity response: {str(e)}")
            return original_analysis
    
    def _calculate_confidence_adjustment(self, insights: str) -> float:
        """Calculate confidence adjustment based on Perplexity insights"""
        try:
            # Simple sentiment analysis of insights
            positive_indicators = ['bullish', 'positive', 'strong', 'favorable', 'opportunity']
            negative_indicators = ['bearish', 'negative', 'weak', 'unfavorable', 'risk']
            
            positive_count = sum(1 for word in positive_indicators if word in insights.lower())
            negative_count = sum(1 for word in negative_indicators if word in insights.lower())
            
            # Calculate adjustment (-0.1 to 0.1)
            adjustment = (positive_count - negative_count) * 0.02
            
            return max(-0.1, min(0.1, adjustment))
            
        except Exception as e:
            logging.error(f"Error calculating confidence adjustment: {str(e)}")
            return 0.0

    def analyze_market(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market conditions and generate trade signals"""
        try:
            # Get enhanced analysis from Perplexity
            perplexity_analysis = self._get_perplexity_analysis(context)
            
            # Analyze options flow
            options_analysis = self._analyze_options_flow(context['options_data'])
            
            # Analyze news sentiment
            news_analysis = self._analyze_news_sentiment(context['news_sentiment'])
            
            # Get sector analysis
            sector_analysis = self._analyze_sector(context['market_data'])
            
            # Combine all analyses
            analysis = {
                'perplexity': perplexity_analysis,
                'options': options_analysis,
                'news': news_analysis,
                'sector': sector_analysis,
                'timestamp': datetime.now().isoformat()
            }
            
            # Generate trade signals
            signals = self._generate_signals(analysis, context['phase'])
            
            return {
                'analysis': analysis,
                'signals': signals,
                'confidence': self._calculate_confidence(analysis)
            }
            
        except Exception as e:
            logging.error(f"Error in market analysis: {str(e)}")
            raise
    
    def _get_perplexity_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get enhanced analysis from Perplexity API"""
        try:
            prompt = self._create_perplexity_prompt(context)
            
            response = requests.post(
                'https://api.perplexity.ai/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.perplexity_api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'pplx-7b-online',
                    'messages': [{'role': 'user', 'content': prompt}]
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Perplexity API error: {response.text}")
                return {}
                
        except Exception as e:
            logging.error(f"Error getting Perplexity analysis: {str(e)}")
            return {}
    
    def _analyze_options_flow(self, options_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze options flow data"""
        try:
            # Implement options flow analysis
            return {
                'call_put_ratio': options_data.get('call_put_ratio', 0),
                'volume_profile': options_data.get('volume_profile', {}),
                'iv_skew': options_data.get('iv_skew', 0),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Error in options flow analysis: {str(e)}")
            return {}
    
    def _analyze_news_sentiment(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze news sentiment data"""
        try:
            # Implement news sentiment analysis
            return {
                'overall_sentiment': news_data.get('overall', 0),
                'recent_headlines': news_data.get('recent_headlines', []),
                'sentiment_trend': news_data.get('sentiment_trend', 0),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Error in news sentiment analysis: {str(e)}")
            return {}
    
    def _analyze_sector(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sector performance and correlations"""
        try:
            # Implement sector analysis
            return {
                'sector_performance': market_data.get('sector_performance', {}),
                'peer_correlations': market_data.get('peer_correlations', {}),
                'sector_trend': market_data.get('sector_trend', 0),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Error in sector analysis: {str(e)}")
            return {}
    
    def _generate_signals(self, analysis: Dict[str, Any], phase: str) -> Dict[str, Any]:
        """Generate trading signals based on analysis"""
        try:
            # Get phase parameters
            phase_params = self.phase_parameters.get(phase, {})
            
            # Generate signals based on analysis and phase
            signals = {
                'entry': self._generate_entry_signals(analysis, phase_params),
                'exit': self._generate_exit_signals(analysis, phase_params),
                'position_size': self._calculate_position_size(analysis, phase_params),
                'timestamp': datetime.now().isoformat()
            }
            
            return signals
            
        except Exception as e:
            logging.error(f"Error generating signals: {str(e)}")
            return {}
    
    def _calculate_confidence(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall confidence level"""
        try:
            # Implement confidence calculation
            return 0.0
        except Exception as e:
            logging.error(f"Error calculating confidence: {str(e)}")
            return 0.0

    def _analyze_technical(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technical indicators"""
        try:
            # Implement technical analysis
            return {}
        except Exception as e:
            logging.error(f"Error in technical analysis: {str(e)}")
            return {}
    
    def _analyze_options(self, options_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze options data"""
        try:
            # Implement options analysis
            return {}
        except Exception as e:
            logging.error(f"Error in options analysis: {str(e)}")
            return {}
    
    def _analyze_sentiment(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze news sentiment"""
        try:
            # Implement sentiment analysis
            return {}
        except Exception as e:
            logging.error(f"Error in sentiment analysis: {str(e)}")
            return {}
    
    def _analyze_fundamental(self, fundamental_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze fundamental data"""
        try:
            # Implement fundamental analysis
            return {}
        except Exception as e:
            logging.error(f"Error in fundamental analysis: {str(e)}")
            return {}
    
    def _analyze_macro(self, macro_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze macroeconomic data"""
        try:
            # Implement macro analysis
            return {}
        except Exception as e:
            logging.error(f"Error in macro analysis: {str(e)}")
            return {}
    
    def _calculate_confidence(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall confidence score"""
        try:
            # Implement confidence calculation
            return 0.0
        except Exception as e:
            logging.error(f"Error calculating confidence: {str(e)}")
            return 0.0 