# Oracle (ORCL) Early Catalyst Phase Trading Analysis

This system analyzes Oracle Corporation (ORCL) for early catalyst phase trading opportunities, focusing on the period 10+ days before earnings announcements.

## Features

- Real-time IV percentile analysis
- Earnings date tracking
- News sentiment analysis using Perplexity AI
- Macro indicators monitoring
- Options flow analysis
- Historical catalyst tracking
- Automated trading recommendations

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```
FMP_API_KEY=your_fmp_api_key
FRED_API_KEY=your_fred_api_key
IBKR_HOST=127.0.0.1
IBKR_PORT=7497
IBKR_CLIENT_ID=123
IBKR_TRUSTED_IP=127.0.0.1
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_user_agent
NEWSAPI_KEY=your_newsapi_key
PERP_API=your_perplexity_api_key
```

## Usage

Run the analysis:
```bash
python oracle_analysis.py
```

The script will:
1. Gather current market data
2. Analyze news and sentiment using Perplexity AI
3. Evaluate catalyst strength
4. Generate trading recommendations

## Output Format

The analysis returns a JSON object with:
- Catalyst summary
- Sentiment score (-100 to +100)
- Recommended action (shares/calls/puts/skip)
- Position size (0-5%)
- Confidence level (0-100)

## Dependencies

- Financial Modeling Prep API
- FRED API
- Interactive Brokers API
- Reddit API
- NewsAPI
- Perplexity API

## Notes

- Ensure all API keys are valid and have sufficient quota
- The system requires an active internet connection
- IBKR connection is optional but recommended for real-time data
- Perplexity API usage will be based on your Perplexity Pro subscription 