# Compound Protocol Wallet Risk Scoring System

A comprehensive risk assessment system for analyzing wallet addresses that interact with Compound V2 and V3 protocols. This system assigns risk scores (0-1000) based on on-chain activity patterns and behavioral indicators.

## Features

- **Multi-API Data Collection**: Uses Etherscan, Alchemy, and The Graph APIs
- **Comprehensive Feature Extraction**: 7 key risk indicators
- **Weighted Risk Scoring**: Sophisticated algorithm with configurable weights
- **Scalable Architecture**: Modular design for processing large wallet lists
- **Detailed Reporting**: CSV output and comprehensive markdown reports

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd wallet-risk-scoring
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Run the setup script
python3 setup.py

# Or manually create .env file from env.example
cp env.example .env
# Then edit .env with your actual API keys
```

## Usage

### Quick Start

Run the complete risk scoring pipeline:

```bash
python main.py
```

This will:
1. Load wallet addresses (currently using sample data)
2. Collect transaction data from Compound protocols
3. Extract risk-relevant features
4. Calculate risk scores (0-1000)
5. Generate CSV output and detailed report

### Output Files

- `wallet_risk_scores_YYYYMMDD_HHMMSS.csv`: Main output with wallet IDs and scores
- `risk_analysis_report_YYYYMMDD_HHMMSS.md`: Detailed analysis report

## Methodology

### Data Collection

The system fetches transaction data from Compound V2 and V3 protocols using:

- **Etherscan API**: Event logs for supply, borrow, repay, withdraw, and liquidation events
- **Alchemy API**: Asset transfer data for comprehensive transaction history
- **The Graph**: Subgraph queries for protocol-specific data

### Feature Extraction

Seven key risk indicators are computed for each wallet:

1. **Borrow-to-Supply Ratio (25%)**: Primary leverage indicator
2. **Liquidation Count (20%)**: Historical risk event frequency
3. **Inactivity Days (15%)**: Recent activity level
4. **Repayment Frequency (15%)**: Behavioral risk indicator
5. **Volatile Asset Usage (10%)**: Asset-specific risk exposure
6. **Protocol Version (10%)**: Technology risk (V3 > V2)
7. **Collateral Factor (5%)**: Safety margin indicator

### Risk Scoring Algorithm

1. **Base Score**: Start with neutral score of 500
2. **Component Scoring**: Each feature contributes -100 to +100 points
3. **Weighted Combination**: Apply configurable weights to each component
4. **Normalization**: Min-max scaling to ensure 0-1000 range
5. **Final Score**: Higher scores indicate lower risk

### Risk Categories

- **800-1000**: Very Low Risk
- **600-799**: Low Risk
- **400-599**: Moderate Risk
- **200-399**: High Risk
- **0-199**: Very High Risk

## Configuration

Edit `config.py` to customize:

- API endpoints and rate limits
- Compound protocol addresses
- Risk scoring weights
- Volatile asset definitions

## Architecture

```
├── main.py              # Main execution script
├── config.py            # Configuration and constants
├── data_collector.py    # Transaction data collection
├── feature_extractor.py # Feature extraction and computation
├── risk_scorer.py       # Risk scoring algorithm
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## API Requirements

### Etherscan API
- Free tier: 5 requests/second
- Used for event logs and block data

### Alchemy API
- Free tier: 10 requests/second
- Used for comprehensive transaction data

### The Graph API
- Free tier available
- Used for protocol-specific queries

## Scalability Considerations

- **Batch Processing**: Process wallets in chunks to manage API limits
- **Caching**: Implement caching for repeated queries
- **Parallel Processing**: Use async/await for concurrent API calls
- **Rate Limiting**: Built-in rate limiting to respect API constraints
- **Error Handling**: Robust error handling and retry logic

## Production Deployment

For production use:

1. **Real Data Integration**: Replace simulated data with actual API calls
2. **Database Storage**: Add database for caching and historical data
3. **Monitoring**: Implement logging and monitoring
4. **Security**: Secure API key management
5. **Performance**: Optimize for large-scale processing

## Example Output

### CSV Format
```csv
wallet_id,score
0xfaa0768bde629806739c3a4620656c5d26f44ef2,732
0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6,845
0x1234567890123456789012345678901234567890,156
```

### Risk Distribution
- Very Low Risk: 15 wallets (15.0%)
- Low Risk: 25 wallets (25.0%)
- Moderate Risk: 35 wallets (35.0%)
- High Risk: 20 wallets (20.0%)
- Very High Risk: 5 wallets (5.0%)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🔒 Security Considerations

- **API Keys**: Stored in environment variables (`.env` file)
- **No Hardcoded Secrets**: All sensitive data is externalized
- **Git Ignore**: `.env` file is excluded from version control
- **Secure Communication**: HTTPS for all API calls
- **Input Validation**: Ethereum address format validation
- **Rate Limiting**: Respects API constraints to avoid abuse

### ⚠️ Important Security Notes

1. **Never commit your `.env` file** - it's already in `.gitignore`
2. **Keep your API keys private** - don't share them publicly
3. **Use environment variables** - never hardcode API keys in code
4. **Rotate keys regularly** - for production use, rotate API keys periodically

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and analytical purposes. Risk scores should not be considered as financial advice. Always conduct thorough due diligence before making investment decisions. 