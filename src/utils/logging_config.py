"""
Logging Configuration Module
Sets up logging for the Oracle earnings trading strategy.
"""

import logging
from datetime import datetime

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        filename='oracle_analysis.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Add console handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def log_run_separator():
    """Add a visual separator for new runs in the log file"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    separator = f"\n{'='*80}\n=== New Analysis Run: {current_time} ===\n{'='*80}\n"
    logging.info(separator) 