"""
Adobe Monitor Module
Handles real-time monitoring and performance tracking.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json
import os

class AdobeMonitor:
    def __init__(self):
        # Monitoring state
        self.metrics = {}
        self.alerts = []
        self.last_update = datetime.min
        
        # Performance tracking
        self.daily_pnl = 0.0
        self.total_pnl = 0.0
        self.max_drawdown = 0.0
        
        # Alert thresholds
        self.thresholds = {
            'daily_loss': -0.05,  # -5% daily loss
            'position_size': 0.10, # 10% max position
            'correlation': 0.70,   # 70% max correlation
            'confidence': 0.60     # 60% min confidence
        }
        
        # Initialize logging
        logging.info("Initialized Adobe Monitor")
    
    def update_metrics(self, data: Dict[str, Any]):
        """Update monitoring metrics"""
        try:
            # Update timestamp
            self.last_update = datetime.now()
            
            # Extract metrics
            analysis = data.get('analysis', {})
            signals = data.get('signals', {})
            positions = data.get('positions', {})
            risk_status = data.get('risk_status', {})
            
            # Calculate performance metrics
            self._update_performance(positions)
            
            # Check for alerts
            self._check_alerts(analysis, risk_status)
            
            # Store metrics
            self.metrics = {
                'timestamp': self.last_update.isoformat(),
                'analysis': analysis,
                'signals': signals,
                'positions': positions,
                'risk_status': risk_status,
                'performance': {
                    'daily_pnl': self.daily_pnl,
                    'total_pnl': self.total_pnl,
                    'max_drawdown': self.max_drawdown
                },
                'alerts': self.alerts
            }
            
            # Log status
            self._log_status()
            
        except Exception as e:
            logging.error(f"Error updating metrics: {str(e)}")
    
    def _update_performance(self, positions: Dict[str, Any]):
        """Update performance metrics"""
        try:
            # Calculate P&L
            total_pnl = sum(float(pos.get('pnl', 0)) for pos in positions.values())
            
            # Update metrics
            self.daily_pnl = total_pnl - self.total_pnl
            self.total_pnl = total_pnl
            
            # Update drawdown
            if self.total_pnl < 0:
                self.max_drawdown = min(self.max_drawdown, self.total_pnl)
            
        except Exception as e:
            logging.error(f"Error updating performance: {str(e)}")
    
    def _check_alerts(self, analysis: Dict[str, Any], risk_status: Dict[str, Any]):
        """Check for alert conditions"""
        try:
            # Clear old alerts
            self.alerts = []
            
            # Check risk status
            for metric, status in risk_status.items():
                if status:
                    self.alerts.append({
                        'type': 'risk',
                        'metric': metric,
                        'message': f"Risk threshold exceeded: {metric}",
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Check confidence
            if analysis.get('confidence', 0) < self.thresholds['confidence']:
                self.alerts.append({
                    'type': 'confidence',
                    'message': "Low confidence in analysis",
                    'timestamp': datetime.now().isoformat()
                })
            
        except Exception as e:
            logging.error(f"Error checking alerts: {str(e)}")
    
    def _log_status(self):
        """Log current status"""
        try:
            status = {
                'timestamp': self.last_update.isoformat(),
                'performance': {
                    'daily_pnl': f"{self.daily_pnl*100:.1f}%",
                    'total_pnl': f"{self.total_pnl*100:.1f}%",
                    'max_drawdown': f"{self.max_drawdown*100:.1f}%"
                },
                'alerts': len(self.alerts)
            }
            
            logging.info(f"Monitor status: {status}")
            
        except Exception as e:
            logging.error(f"Error logging status: {str(e)}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get current alerts"""
        return self.alerts 