"""
Phase Controller Module
Manages the flow between different phases of the Oracle earnings trading strategy.
"""

from datetime import datetime
import logging
from typing import Dict, Any

class PhaseController:
    """Controls the flow between different phases of the Oracle earnings trading strategy"""
    
    def __init__(self):
        self.current_phase = None
        self.phase_history = []
        self.phase_transitions = {
            "early_catalyst": {
                "next_phase": "momentum_volatility",
                "condition": lambda days: days <= 9
            },
            "momentum_volatility": {
                "next_phase": "final_pre_earnings",
                "condition": lambda days: days <= 4
            },
            "final_pre_earnings": {
                "next_phase": "post_earnings",
                "condition": lambda days: days <= 0
            },
            "post_earnings": {
                "next_phase": "no_setup",
                "condition": lambda days: days <= -2
            }
        }
        
        # Phase-specific risk parameters
        self.phase_risk_params = {
            "early_catalyst": {
                "max_position_size": "3%",
                "max_iv_percentile": 75,
                "min_catalyst_strength": 60
            },
            "momentum_volatility": {
                "max_position_size": "3%",
                "max_iv_percentile": 85,
                "min_momentum_score": 0.5
            },
            "final_pre_earnings": {
                "max_position_size": "1%",
                "max_iv_percentile": 90,
                "require_spreads": True
            },
            "post_earnings": {
                "max_position_size": "2%",
                "max_iv_percentile": 70,
                "min_confidence": 70
            },
            "no_setup": {
                "max_position_size": "0%",
                "skip_threshold": 60
            }
        }
    
    def determine_phase(self, days_to_earnings: int) -> str:
        """Determine the current phase based on days to earnings"""
        if days_to_earnings > 9:
            return "early_catalyst"
        elif days_to_earnings > 4:
            return "momentum_volatility"
        elif days_to_earnings > 0:
            return "final_pre_earnings"
        elif days_to_earnings >= -2:
            return "post_earnings"
        else:
            return "no_setup"
    
    def check_phase_transition(self, current_phase: str, days_to_earnings: int) -> bool:
        """Check if a phase transition should occur"""
        if current_phase not in self.phase_transitions:
            return False
        
        transition = self.phase_transitions[current_phase]
        return transition["condition"](days_to_earnings)
    
    def get_next_phase(self, current_phase: str) -> str:
        """Get the next phase in the sequence"""
        return self.phase_transitions.get(current_phase, {}).get("next_phase", "no_setup")
    
    def get_phase_risk_params(self, phase: str) -> Dict[str, Any]:
        """Get risk parameters for a specific phase"""
        return self.phase_risk_params.get(phase, self.phase_risk_params["no_setup"])
    
    def log_phase_transition(self, from_phase: str, to_phase: str, days_to_earnings: int):
        """Log phase transition details"""
        transition = {
            "timestamp": datetime.now().isoformat(),
            "from_phase": from_phase,
            "to_phase": to_phase,
            "days_to_earnings": days_to_earnings
        }
        self.phase_history.append(transition)
        logging.info(f"Phase transition: {from_phase} -> {to_phase} (Days to earnings: {days_to_earnings})") 