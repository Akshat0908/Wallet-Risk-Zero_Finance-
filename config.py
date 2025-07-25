import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY', '')
ALCHEMY_API_KEY = os.getenv('ALCHEMY_API_KEY', '')
THE_GRAPH_API_KEY = os.getenv('THE_GRAPH_API_KEY', '')

# Compound Protocol Addresses
COMPOUND_V2_COMPTROLLER = "0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B"
COMPOUND_V3_COMPTROLLER = "0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B"

# Compound V2 Market Addresses
COMPOUND_V2_MARKETS = {
    "cDAI": "0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643",
    "cUSDC": "0x39AA39c021dfbaE8faC545936693aC917d5E7563",
    "cETH": "0x4Ddc2D193948926D02f9B1fE9e1daa0718270ED5",
    "cWBTC": "0xC11b1268C1A384e55C48c2391d8d480264A3A7F4",
    "cUSDT": "0xf650C3d88D12dB855b8bf7D11Be6C55A4e07dCC9",
    "cCOMP": "0x70e36f6BF80a52b3B46b3aF8e106CC0ed743E8e4",
    "cUNI": "0x35A18000230DA775CAc24873d00Ff85BccdeD550",
    "cLINK": "0xFAce851a4921ce59e912d19329929CE6da6EB0c7",
    "cMKR": "0x95b4eF2869eBD94BEb4eEE400a97824Af4F4Ab1c",
    "cYFI": "0x80a2AE356fc9ef4305676f7a3E2Ed04e12C33946",
    "cBAT": "0x6C8c6b02E7b2BE14d4fA6022Dfd6d75921D90E4E",
    "cZRX": "0xB3319f5D18Bc0D84dD1b4825Dcde5d5f7266d407",
    "cAAVE": "0xe65cdB6479BaC1e22340E4E755fAE7E509EcD06c",
    "cSUSHI": "0x4B0181102A0112A2ef11AbEE5563bb4a3176c9d7"
}

# Compound V3 Market Addresses
COMPOUND_V3_MARKETS = {
    "USDC": "0xc3d688B66703497DAA19211EEdff47f25384cdc3",
    "WETH": "0xA17581A9E3356d9A858b789D68B4d7eD7D5b8A6A",
    "WBTC": "0xccF4429DB6322D5C611ee964527D42E5d685DD6a",
    "LINK": "0x9c4ec768c28520B50860ea7a15bd7213a9fF58bf",
    "UNI": "0x9a0242b7a33DAcbe44eD41d3A2b3b3a3C3b3b3b3"
}

# Risk Scoring Weights
RISK_WEIGHTS = {
    'borrow_supply_ratio': 0.25,
    'liquidation_count': 0.20,
    'inactivity_days': 0.15,
    'repayment_frequency': 0.15,
    'volatile_asset_usage': 0.10,
    'protocol_version': 0.10,
    'collateral_factor': 0.05
}

# Volatile Assets (higher risk)
VOLATILE_ASSETS = ['WBTC', 'ETH', 'LINK', 'UNI', 'MKR', 'YFI', 'AAVE', 'SUSHI']

# API Rate Limits
ETHERSCAN_RATE_LIMIT = 5  # requests per second
ALCHEMY_RATE_LIMIT = 10   # requests per second 