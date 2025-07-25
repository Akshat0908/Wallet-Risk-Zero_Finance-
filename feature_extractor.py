import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from config import *

class FeatureExtractor:
    """
    Extract and compute risk-relevant features from Compound transaction data
    """
    
    def __init__(self):
        self.volatile_assets = VOLATILE_ASSETS
        self.v2_markets = COMPOUND_V2_MARKETS
        self.v3_markets = COMPOUND_V3_MARKETS
    
    def extract_wallet_features(self, transactions_df: pd.DataFrame, wallet_address: str) -> Dict:
        """
        Extract comprehensive features for a single wallet
        """
        if transactions_df.empty:
            return self._get_default_features(wallet_address)
        
        # Filter transactions for this wallet
        wallet_txs = transactions_df[transactions_df['wallet'] == wallet_address].copy()
        
        if wallet_txs.empty:
            return self._get_default_features(wallet_address)
        
        features = {
            'wallet_id': wallet_address,
            'total_transactions': len(wallet_txs),
            'first_transaction_date': wallet_txs['timestamp'].min(),
            'last_transaction_date': wallet_txs['timestamp'].max(),
            'days_since_last_activity': self._calculate_inactivity_days(wallet_txs),
            'total_supplied_usd': self._calculate_total_supplied(wallet_txs),
            'total_borrowed_usd': self._calculate_total_borrowed(wallet_txs),
            'supply_to_borrow_ratio': 0.0,
            'number_of_liquidations': self._count_liquidations(wallet_txs),
            'repayment_frequency': self._calculate_repayment_frequency(wallet_txs),
            'volatile_asset_usage': self._calculate_volatile_asset_usage(wallet_txs),
            'protocol_version_usage': self._determine_protocol_version(wallet_txs),
            'collateral_factor_average': self._calculate_collateral_factor(wallet_txs),
            'borrowing_behavior': self._analyze_borrowing_behavior(wallet_txs),
            'health_factor_trend': self._calculate_health_factor_trend(wallet_txs)
        }
        
        # Calculate supply to borrow ratio
        if features['total_supplied_usd'] > 0:
            features['supply_to_borrow_ratio'] = features['total_borrowed_usd'] / features['total_supplied_usd']
        
        return features
    
    def _get_default_features(self, wallet_address: str) -> Dict:
        """
        Return default features for wallets with no transactions
        """
        return {
            'wallet_id': wallet_address,
            'total_transactions': 0,
            'first_transaction_date': None,
            'last_transaction_date': None,
            'days_since_last_activity': 365,  # High inactivity penalty
            'total_supplied_usd': 0,
            'total_borrowed_usd': 0,
            'supply_to_borrow_ratio': 0,
            'number_of_liquidations': 0,
            'repayment_frequency': 0,
            'volatile_asset_usage': 0,
            'protocol_version_usage': 'none',
            'collateral_factor_average': 0,
            'borrowing_behavior': 'none',
            'health_factor_trend': 'stable'
        }
    
    def _calculate_inactivity_days(self, wallet_txs: pd.DataFrame) -> int:
        """
        Calculate days since last activity
        """
        if wallet_txs.empty:
            return 365
        
        last_activity = wallet_txs['timestamp'].max()
        current_time = datetime.now()
        return (current_time - last_activity).days
    
    def _calculate_total_supplied(self, wallet_txs: pd.DataFrame) -> float:
        """
        Calculate total USD value supplied to Compound
        """
        # This is a simplified calculation. In production, you'd need to:
        # 1. Parse the actual event data to get amounts
        # 2. Convert to USD using price feeds
        # 3. Handle different asset types
        
        supply_events = wallet_txs[
            wallet_txs['market'].str.contains('c', na=False) | 
            wallet_txs['market'].isin(['USDC', 'WETH', 'WBTC'])
        ]
        
        # Simplified: assume each supply event is worth $1000 on average
        return len(supply_events) * 1000
    
    def _calculate_total_borrowed(self, wallet_txs: pd.DataFrame) -> float:
        """
        Calculate total USD value borrowed from Compound
        """
        # Similar to supply calculation but for borrow events
        borrow_events = wallet_txs[
            wallet_txs['market'].str.contains('c', na=False) | 
            wallet_txs['market'].isin(['USDC', 'WETH', 'WBTC'])
        ]
        
        # Simplified: assume each borrow event is worth $500 on average
        return len(borrow_events) * 500
    
    def _count_liquidations(self, wallet_txs: pd.DataFrame) -> int:
        """
        Count liquidation events where this wallet was the borrower
        """
        # Look for liquidation events in transaction data
        liquidation_events = wallet_txs[
            wallet_txs['market'].str.contains('liquidate', case=False, na=False) |
            wallet_txs['topics'].apply(lambda x: any('liquidate' in str(topic).lower() for topic in x) if isinstance(x, list) else False)
        ]
        
        return len(liquidation_events)
    
    def _calculate_repayment_frequency(self, wallet_txs: pd.DataFrame) -> float:
        """
        Calculate repayment frequency (repayments per month)
        """
        if wallet_txs.empty:
            return 0
        
        # Identify repayment events
        repayment_events = wallet_txs[
            wallet_txs['market'].str.contains('repay', case=False, na=False) |
            wallet_txs['topics'].apply(lambda x: any('repay' in str(topic).lower() for topic in x) if isinstance(x, list) else False)
        ]
        
        if repayment_events.empty:
            return 0
        
        # Calculate time span of activity
        time_span = (wallet_txs['timestamp'].max() - wallet_txs['timestamp'].min()).days
        
        if time_span == 0:
            return len(repayment_events)
        
        # Convert to repayments per month
        months_active = time_span / 30
        return len(repayment_events) / months_active if months_active > 0 else 0
    
    def _calculate_volatile_asset_usage(self, wallet_txs: pd.DataFrame) -> float:
        """
        Calculate percentage of transactions involving volatile assets
        """
        if wallet_txs.empty:
            return 0
        
        volatile_transactions = wallet_txs[
            wallet_txs['market'].apply(lambda x: any(asset in str(x).upper() for asset in self.volatile_assets))
        ]
        
        return len(volatile_transactions) / len(wallet_txs)
    
    def _determine_protocol_version(self, wallet_txs: pd.DataFrame) -> str:
        """
        Determine which protocol version the wallet primarily uses
        """
        if wallet_txs.empty:
            return 'none'
        
        v2_transactions = wallet_txs[wallet_txs['market'].isin(self.v2_markets.keys())]
        v3_transactions = wallet_txs[wallet_txs['market'].isin(self.v3_markets.keys())]
        
        if len(v3_transactions) > len(v2_transactions):
            return 'v3'
        elif len(v2_transactions) > 0:
            return 'v2'
        else:
            return 'unknown'
    
    def _calculate_collateral_factor(self, wallet_txs: pd.DataFrame) -> float:
        """
        Calculate average collateral factor (simplified)
        """
        if wallet_txs.empty:
            return 0
        
        # Simplified calculation based on asset types
        # In production, you'd query the actual collateral factors from the protocol
        
        collateral_factors = {
            'USDC': 0.85, 'USDT': 0.80, 'DAI': 0.85,  # Stablecoins
            'ETH': 0.75, 'WETH': 0.75, 'WBTC': 0.70,  # Major assets
            'LINK': 0.65, 'UNI': 0.60, 'MKR': 0.55,   # DeFi tokens
            'YFI': 0.50, 'AAVE': 0.55, 'SUSHI': 0.50  # More volatile
        }
        
        total_factor = 0
        count = 0
        
        for _, tx in wallet_txs.iterrows():
            market = str(tx['market']).upper()
            for asset, factor in collateral_factors.items():
                if asset in market:
                    total_factor += factor
                    count += 1
                    break
        
        return total_factor / count if count > 0 else 0
    
    def _analyze_borrowing_behavior(self, wallet_txs: pd.DataFrame) -> str:
        """
        Analyze borrowing behavior patterns
        """
        if wallet_txs.empty:
            return 'none'
        
        # Count different types of transactions
        supply_count = len(wallet_txs[wallet_txs['market'].str.contains('mint|supply', case=False, na=False)])
        borrow_count = len(wallet_txs[wallet_txs['market'].str.contains('borrow', case=False, na=False)])
        repay_count = len(wallet_txs[wallet_txs['market'].str.contains('repay', case=False, na=False)])
        
        if borrow_count == 0:
            return 'supplier_only'
        elif supply_count == 0:
            return 'borrower_only'
        elif repay_count / max(borrow_count, 1) > 0.8:
            return 'responsible_borrower'
        else:
            return 'risky_borrower'
    
    def _calculate_health_factor_trend(self, wallet_txs: pd.DataFrame) -> str:
        """
        Calculate health factor trend (simplified)
        """
        if wallet_txs.empty:
            return 'unknown'
        
        # Simplified health factor calculation
        # In production, you'd calculate actual health factors over time
        
        recent_txs = wallet_txs.tail(10)  # Last 10 transactions
        older_txs = wallet_txs.head(max(1, len(wallet_txs) - 10))  # Earlier transactions
        
        recent_volatility = self._calculate_volatile_asset_usage(recent_txs)
        older_volatility = self._calculate_volatile_asset_usage(older_txs)
        
        if recent_volatility < older_volatility:
            return 'improving'
        elif recent_volatility > older_volatility:
            return 'deteriorating'
        else:
            return 'stable'
    
    def extract_all_wallet_features(self, transactions_df: pd.DataFrame, wallet_addresses: List[str]) -> pd.DataFrame:
        """
        Extract features for all wallets
        """
        all_features = []
        
        for wallet in wallet_addresses:
            features = self.extract_wallet_features(transactions_df, wallet)
            all_features.append(features)
        
        return pd.DataFrame(all_features) 