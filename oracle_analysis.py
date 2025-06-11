"""
Oracle Earnings Trading Strategy - Main Module
This module serves as the entry point for the Oracle earnings trading strategy.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
import logging

# Import from our modules
from src.phase_controller import PhaseController
from src.analyzer import OracleAnalyzer
from src.monitor import StrategyMonitor
from src.utils.logging_config import setup_logging

def main():
    """Main entry point for the Oracle earnings trading strategy"""
    # Set up logging
    setup_logging()
    
    # Load environment variables
    load_dotenv()
    
    # Initialize components
    monitor = StrategyMonitor()
    analyzer = OracleAnalyzer(monitor)
    
    # Run analysis
    result = analyzer.analyze_oracle()
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main() 