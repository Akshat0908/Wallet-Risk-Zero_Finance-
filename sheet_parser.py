import requests
import pandas as pd
from typing import List
import re

def parse_google_sheet(sheet_url: str) -> List[str]:
    """
    Parse wallet addresses from Google Sheets URL
    
    Args:
        sheet_url: Google Sheets URL containing wallet addresses
        
    Returns:
        List of wallet addresses
    """
    try:
        # Extract sheet ID from URL
        sheet_id = extract_sheet_id(sheet_url)
        
        # Convert to CSV export URL
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        
        # Download the CSV data
        response = requests.get(csv_url)
        response.raise_for_status()
        
        # Parse CSV data
        from io import StringIO
        df = pd.read_csv(StringIO(response.text))
        
        # Extract wallet addresses (assuming they're in the first column)
        wallet_addresses = []
        
        for _, row in df.iterrows():
            # Get the first non-empty value from the row
            for value in row.values:
                if pd.notna(value) and str(value).strip():
                    address = str(value).strip()
                    # Validate Ethereum address format
                    if is_valid_ethereum_address(address):
                        wallet_addresses.append(address)
                    break
        
        return wallet_addresses
        
    except Exception as e:
        print(f"Error parsing Google Sheet: {e}")
        return []

def extract_sheet_id(url: str) -> str:
    """
    Extract sheet ID from Google Sheets URL
    """
    # Pattern to match Google Sheets URL
    pattern = r'/spreadsheets/d/([a-zA-Z0-9-_]+)'
    match = re.search(pattern, url)
    
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Google Sheets URL format")

def is_valid_ethereum_address(address: str) -> bool:
    """
    Validate Ethereum address format
    """
    # Check if it's a valid Ethereum address (0x followed by 40 hex characters)
    pattern = r'^0x[a-fA-F0-9]{40}$'
    return bool(re.match(pattern, address))

def load_wallets_from_sheet(sheet_url: str) -> List[str]:
    """
    Load wallet addresses from Google Sheets with fallback to sample data
    """
    print(f"Attempting to load wallets from: {sheet_url}")
    
    # Try to parse the actual sheet
    wallets = parse_google_sheet(sheet_url)
    
    if wallets:
        print(f"Successfully loaded {len(wallets)} wallet addresses from Google Sheets")
        return wallets
    else:
        print("Failed to load from Google Sheets, using sample data")
        return get_sample_wallets()

def get_sample_wallets() -> List[str]:
    """
    Return sample wallet addresses for testing
    """
    return [
        "0xfaa0768bde629806739c3a4620656c5d26f44ef2",
        "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
        "0x1234567890123456789012345678901234567890",
        "0xabcdef1234567890abcdef1234567890abcdef12",
        "0x9876543210987654321098765432109876543210",
        "0x1111111111111111111111111111111111111111",
        "0x2222222222222222222222222222222222222222",
        "0x3333333333333333333333333333333333333333",
        "0x4444444444444444444444444444444444444444",
        "0x5555555555555555555555555555555555555555",
        "0x6666666666666666666666666666666666666666",
        "0x7777777777777777777777777777777777777777",
        "0x8888888888888888888888888888888888888888",
        "0x9999999999999999999999999999999999999999",
        "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "0xcccccccccccccccccccccccccccccccccccccccc",
        "0xdddddddddddddddddddddddddddddddddddddddd",
        "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        "0xffffffffffffffffffffffffffffffffffffffff"
    ]

if __name__ == "__main__":
    # Test the sheet parser
    test_url = "https://docs.google.com/spreadsheets/d/1ZzaeMgNYnxvriYYpe8PE7uMEblTI0GV5GIVUnsP-sBs/edit?usp=sharing"
    
    wallets = load_wallets_from_sheet(test_url)
    print(f"Loaded {len(wallets)} wallets:")
    for i, wallet in enumerate(wallets[:5]):  # Show first 5
        print(f"  {i+1}. {wallet}")
    if len(wallets) > 5:
        print(f"  ... and {len(wallets) - 5} more") 