"""
Oracle Backtesting Module
Handles historical strategy testing and performance analysis.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from src.data_client import DataClient
from src.risk_engine import OracleRiskEngine

class OracleBacktest:
    def __init__(self, start_date: datetime, end_date: datetime):
        self.start_date = start_date
        self.end_date = end_date
        self.data_client = DataClient()
        self.risk_engine = OracleRiskEngine()
        
        # Performance tracking
        self.trades = []
        self.positions = []
        self.daily_pnl = []
        
        # Commission and slippage assumptions
        self.commission_per_trade = 1.0  # $1 per trade
        self.slippage_percent = 0.001  # 0.1% slippage
    
    def backtest_strategy(self) -> Dict[str, Any]:
        """
        Run backtest of the Oracle earnings strategy
        
        Returns:
            Dictionary containing backtest results
        """
        try:
            # Get historical data
            historical_data = self._get_historical_data()
            
            # Initialize tracking
            current_date = self.start_date
            portfolio_value = 100000  # Start with $100k
            positions = []
            
            while current_date <= self.end_date:
                # Get data for current date
                date_data = self._get_date_data(historical_data, current_date)
                
                # Calculate days to earnings
                days_to_earnings = self._calculate_days_to_earnings(current_date, date_data)
                
                # Determine phase
                phase = self._determine_phase(days_to_earnings)
                
                # Get phase-specific analysis
                analysis = self._analyze_phase(phase, date_data, days_to_earnings)
                
                # Check risk parameters
                risk_check = self.risk_engine.check_circuit_breakers(analysis)
                
                if risk_check['can_proceed']:
                    # Execute trade
                    trade = self._execute_trade(analysis, date_data, portfolio_value)
                    self.trades.append(trade)
                    
                    # Update positions
                    positions = self._update_positions(positions, trade)
                    self.positions.append(positions.copy())
                    
                    # Calculate P&L
                    daily_pnl = self._calculate_daily_pnl(positions, date_data)
                    self.daily_pnl.append({
                        'date': current_date,
                        'pnl': daily_pnl,
                        'portfolio_value': portfolio_value + daily_pnl
                    })
                    
                    # Update portfolio value
                    portfolio_value += daily_pnl
                
                # Move to next date
                current_date += timedelta(days=1)
            
            # Calculate performance metrics
            metrics = self._calculate_performance_metrics()
            
            return {
                'start_date': self.start_date.isoformat(),
                'end_date': self.end_date.isoformat(),
                'initial_capital': 100000,
                'final_capital': portfolio_value,
                'total_return': (portfolio_value - 100000) / 100000,
                'metrics': metrics,
                'trades': self.trades,
                'daily_pnl': self.daily_pnl
            }
            
        except Exception as e:
            logging.error(f"Error in backtest: {str(e)}")
            return {
                'error': str(e),
                'start_date': self.start_date.isoformat(),
                'end_date': self.end_date.isoformat()
            }
    
    def _get_historical_data(self) -> Dict[str, Any]:
        """Get historical data for backtesting"""
        try:
            # Get earnings history
            earnings = self.data_client.get_earnings_history()
            
            # Get historical prices
            prices = self.data_client.get_volume_data()
            
            # Get historical options data
            options = self.data_client.get_options_data()
            
            return {
                'earnings': earnings,
                'prices': prices,
                'options': options
            }
            
        except Exception as e:
            logging.error(f"Error getting historical data: {str(e)}")
            return {}
    
    def _get_date_data(self, historical_data: Dict[str, Any], date: datetime) -> Dict[str, Any]:
        """Get data for specific date"""
        try:
            # Filter data for specific date
            date_str = date.strftime('%Y-%m-%d')
            
            prices = historical_data.get('prices', {}).get('historical_volume', [])
            date_prices = [p for p in prices if p['date'] == date_str]
            
            options = historical_data.get('options', {}).get('options_chain', [])
            date_options = [o for o in options if o['date'] == date_str]
            
            return {
                'prices': date_prices[0] if date_prices else None,
                'options': date_options[0] if date_options else None
            }
            
        except Exception as e:
            logging.error(f"Error getting date data: {str(e)}")
            return {}
    
    def _calculate_days_to_earnings(self, current_date: datetime, date_data: Dict[str, Any]) -> int:
        """Calculate days until next earnings"""
        try:
            earnings = date_data.get('earnings', [])
            if not earnings:
                return 5  # Default fallback
            
            # Get next earnings date
            earnings_dates = [
                datetime.strptime(earning['date'], '%Y-%m-%d')
                for earning in earnings
            ]
            earnings_dates.sort()
            
            # Find next earnings date
            for date in earnings_dates:
                if date > current_date:
                    return (date - current_date).days
            
            return 5  # Default fallback
            
        except Exception as e:
            logging.error(f"Error calculating days to earnings: {str(e)}")
            return 5
    
    def _determine_phase(self, days_to_earnings: int) -> str:
        """Determine trading phase based on days to earnings"""
        if days_to_earnings > 10:
            return "early_catalyst"
        elif days_to_earnings > 4:
            return "momentum_volatility"
        elif days_to_earnings > 0:
            return "final_pre_earnings"
        else:
            return "post_earnings"
    
    def _analyze_phase(self, phase: str, date_data: Dict[str, Any], days_to_earnings: int) -> Dict[str, Any]:
        """Analyze current phase and generate trading signals"""
        try:
            if phase == "early_catalyst":
                return self._analyze_early_catalyst(date_data)
            elif phase == "momentum_volatility":
                return self._analyze_momentum_volatility(date_data)
            elif phase == "final_pre_earnings":
                return self._analyze_final_pre_earnings(date_data)
            else:
                return self._analyze_post_earnings(date_data)
                
        except Exception as e:
            logging.error(f"Error analyzing phase: {str(e)}")
            return {
                'action': 'skip',
                'confidence': 0
            }
    
    def _execute_trade(self, analysis: Dict[str, Any], date_data: Dict[str, Any], portfolio_value: float) -> Dict[str, Any]:
        """Execute trade based on analysis"""
        try:
            # Calculate position size
            size = self.risk_engine.calculate_max_size(
                analysis.get('confidence', 0),
                date_data.get('iv_rank', 0.5)
            )
            
            # Apply slippage
            price = date_data['prices']['close'] * (1 + self.slippage_percent)
            
            # Calculate commission
            commission = self.commission_per_trade
            
            return {
                'date': date_data['prices']['date'],
                'action': analysis['action'],
                'size': size,
                'price': price,
                'commission': commission,
                'confidence': analysis.get('confidence', 0)
            }
            
        except Exception as e:
            logging.error(f"Error executing trade: {str(e)}")
            return {
                'date': date_data['prices']['date'],
                'action': 'skip',
                'error': str(e)
            }
    
    def _update_positions(self, current_positions: List[Dict[str, Any]], trade: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Update positions after trade"""
        try:
            if trade['action'] == 'skip':
                return current_positions
            
            # Add new position
            current_positions.append({
                'date': trade['date'],
                'action': trade['action'],
                'size': trade['size'],
                'price': trade['price']
            })
            
            return current_positions
            
        except Exception as e:
            logging.error(f"Error updating positions: {str(e)}")
            return current_positions
    
    def _calculate_daily_pnl(self, positions: List[Dict[str, Any]], date_data: Dict[str, Any]) -> float:
        """Calculate daily P&L"""
        try:
            pnl = 0
            
            for position in positions:
                if position['action'] == 'long_shares':
                    pnl += float(position['size'].strip('%')) * (date_data['prices']['close'] - position['price'])
                elif position['action'] in ['long_calls', 'long_puts']:
                    # Simplified options P&L calculation
                    pnl += float(position['size'].strip('%')) * (date_data['options']['price'] - position['price'])
            
            return pnl
            
        except Exception as e:
            logging.error(f"Error calculating daily P&L: {str(e)}")
            return 0
    
    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics"""
        try:
            # Convert daily P&L to DataFrame
            df = pd.DataFrame(self.daily_pnl)
            
            # Calculate returns
            returns = df['pnl'] / df['portfolio_value'].shift(1)
            
            # Calculate metrics
            total_return = (df['portfolio_value'].iloc[-1] - df['portfolio_value'].iloc[0]) / df['portfolio_value'].iloc[0]
            sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std()
            max_drawdown = (df['portfolio_value'] / df['portfolio_value'].cummax() - 1).min()
            win_rate = len([t for t in self.trades if t.get('pnl', 0) > 0]) / len(self.trades)
            
            return {
                'total_return': f"{total_return*100:.1f}%",
                'sharpe_ratio': f"{sharpe_ratio:.2f}",
                'max_drawdown': f"{max_drawdown*100:.1f}%",
                'win_rate': f"{win_rate*100:.1f}%",
                'total_trades': len(self.trades)
            }
            
        except Exception as e:
            logging.error(f"Error calculating performance metrics: {str(e)}")
            return {
                'error': str(e)
            } 