import requests
import time
import asyncio
import aiohttp
from typing import List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
from config import *

class CompoundDataCollector:
    """
    Data collector for Compound V2/V3 protocol transactions
    """
    
    def __init__(self):
        self.etherscan_base_url = "https://api.etherscan.io/api"
        self.alchemy_base_url = f"https://worldchain-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
        self.session = requests.Session()
        
    def get_wallet_transactions_etherscan(self, wallet_address: str, start_block: int = 0) -> List[Dict]:
        """
        Fetch Compound-related transactions for a wallet using Etherscan API
        """
        transactions = []
        
        # Compound V2 events to track
        v2_events = [
            "Mint(address,uint256,uint256)",  # Supply
            "Redeem(address,uint256,uint256)",  # Withdraw
            "Borrow(address,uint256,uint256,uint256)",  # Borrow
            "RepayBorrow(address,address,uint256,uint256)",  # Repay
            "LiquidateBorrow(address,address,uint256,address,uint256)"  # Liquidation
        ]
        
        # Compound V3 events to track
        v3_events = [
            "Supply(address,address,uint256,uint256)",  # Supply
            "Withdraw(address,address,uint256,uint256)",  # Withdraw
            "Borrow(address,address,uint256,uint256,uint256)",  # Borrow
            "Repay(address,address,uint256,uint256)",  # Repay
            "Liquidate(address,address,uint256,uint256,uint256)"  # Liquidation
        ]
        
        # Get transactions for each market
        all_markets = {**COMPOUND_V2_MARKETS, **COMPOUND_V3_MARKETS}
        
        for market_name, market_address in all_markets.items():
            try:
                # Get logs for this market
                params = {
                    'module': 'logs',
                    'action': 'getLogs',
                    'address': market_address,
                    'fromBlock': start_block,
                    'toBlock': 'latest',
                    'apikey': ETHERSCAN_API_KEY
                }
                
                response = self.session.get(self.etherscan_base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data['status'] == '1' and data['result']:
                    for log in data['result']:
                        # Check if wallet is involved in the transaction
                        if wallet_address.lower() in log['topics'] or wallet_address.lower() in log['data']:
                            transaction = {
                                'wallet': wallet_address,
                                'market': market_name,
                                'market_address': market_address,
                                'block_number': int(log['blockNumber'], 16),
                                'transaction_hash': log['transactionHash'],
                                'log_index': int(log['logIndex'], 16),
                                'topics': log['topics'],
                                'data': log['data'],
                                'timestamp': self._get_block_timestamp(int(log['blockNumber'], 16))
                            }
                            transactions.append(transaction)
                
                # Rate limiting
                time.sleep(1 / ETHERSCAN_RATE_LIMIT)
                
            except Exception as e:
                print(f"Error fetching data for market {market_name}: {e}")
                continue
        
        return transactions
    
    def _get_block_timestamp(self, block_number: int) -> int:
        """
        Get block timestamp using Etherscan API
        """
        try:
            params = {
                'module': 'proxy',
                'action': 'eth_getBlockByNumber',
                'tag': hex(block_number),
                'boolean': 'false',
                'apikey': ETHERSCAN_API_KEY
            }
            
            response = self.session.get(self.etherscan_base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['result']:
                return int(data['result']['timestamp'], 16)
            
        except Exception as e:
            print(f"Error getting block timestamp: {e}")
        
        return 0
    
    async def get_wallet_transactions_alchemy(self, wallet_address: str) -> List[Dict]:
        """
        Fetch Compound transactions using Alchemy API (async)
        """
        transactions = []
        
        async with aiohttp.ClientSession() as session:
            # Get all transactions for the wallet
            url = f"{self.alchemy_base_url}/getAssetTransfers"
            payload = {
                "jsonrpc": "2.0",
                "method": "alchemy_getAssetTransfers",
                "params": [
                    {
                        "fromBlock": "0x0",
                        "toBlock": "latest",
                        "category": ["external", "internal"],
                        "withMetadata": True,
                        "excludeZeroValue": False,
                        "maxCount": "0x3e8"
                    }
                ],
                "id": 1
            }
            
            try:
                async with session.post(url, json=payload) as response:
                    data = await response.json()
                    
                    if 'result' in data and 'transfers' in data['result']:
                        for transfer in data['result']['transfers']:
                            # Check if transaction involves Compound markets
                            if self._is_compound_transaction(transfer):
                                transaction = {
                                    'wallet': wallet_address,
                                    'transaction_hash': transfer['hash'],
                                    'block_number': int(transfer['blockNum'], 16),
                                    'timestamp': int(transfer['metadata']['blockTimestamp']),
                                    'from': transfer['from'],
                                    'to': transfer['to'],
                                    'value': transfer['value'],
                                    'asset': transfer['asset']
                                }
                                transactions.append(transaction)
                                
            except Exception as e:
                print(f"Error fetching Alchemy data: {e}")
        
        return transactions
    
    def _is_compound_transaction(self, transfer: Dict) -> bool:
        """
        Check if a transaction involves Compound protocol
        """
        compound_addresses = list(COMPOUND_V2_MARKETS.values()) + list(COMPOUND_V3_MARKETS.values())
        compound_addresses.extend([COMPOUND_V2_COMPTROLLER, COMPOUND_V3_COMPTROLLER])
        
        from_addr = transfer.get('from', '').lower()
        to_addr = transfer.get('to', '').lower()
        
        return any(addr.lower() in [from_addr, to_addr] for addr in compound_addresses)
    
    def get_wallet_list_from_sheet(self, sheet_url: str) -> List[str]:
        """
        Extract wallet addresses from Google Sheets URL
        For now, we'll use a sample list. In production, you'd parse the actual sheet.
        """
        # Sample wallet addresses (replace with actual sheet parsing)
        sample_wallets = [
            "0xfaa0768bde629806739c3a4620656c5d26f44ef2",
            "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "0x1234567890123456789012345678901234567890",
            # Add more sample addresses here
        ]
        
        return sample_wallets
    
    def collect_all_wallet_data(self, wallet_addresses: List[str]) -> pd.DataFrame:
        """
        Collect transaction data for all wallets
        """
        all_transactions = []
        
        for i, wallet in enumerate(wallet_addresses):
            print(f"Processing wallet {i+1}/{len(wallet_addresses)}: {wallet}")
            
            # Get transactions from Etherscan
            transactions = self.get_wallet_transactions_etherscan(wallet)
            all_transactions.extend(transactions)
            
            # Rate limiting between wallets
            time.sleep(2)
        
        # Convert to DataFrame
        df = pd.DataFrame(all_transactions)
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df = df.sort_values('timestamp')
        
        return df 