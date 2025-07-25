import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from sklearn.preprocessing import MinMaxScaler
from config import *

class RiskScorer:
    """
    Risk scoring model for Compound protocol wallets
    """
    
    def __init__(self):
        self.weights = RISK_WEIGHTS
        self.scaler = MinMaxScaler()
        
    def calculate_risk_score(self, features: Dict) -> int:
        """
        Calculate risk score (0-1000) for a single wallet
        """
        # Initialize base score
        base_score = 500  # Start with neutral score
        
        # Calculate individual risk components
        risk_components = {
            'borrow_supply_ratio': self._score_borrow_supply_ratio(features),
            'liquidation_count': self._score_liquidation_count(features),
            'inactivity_days': self._score_inactivity_days(features),
            'repayment_frequency': self._score_repayment_frequency(features),
            'volatile_asset_usage': self._score_volatile_asset_usage(features),
            'protocol_version': self._score_protocol_version(features),
            'collateral_factor': self._score_collateral_factor(features)
        }
        
        # Apply weighted scoring
        weighted_score = 0
        for component, score in risk_components.items():
            weight = self.weights.get(component, 0)
            weighted_score += score * weight
        
        # Calculate final score
        final_score = base_score + weighted_score
        
        # Ensure score is within 0-1000 range
        final_score = max(0, min(1000, final_score))
        
        return int(final_score)
    
    def _score_borrow_supply_ratio(self, features: Dict) -> float:
        """
        Score based on borrow to supply ratio
        Lower ratio = lower risk = higher score
        """
        ratio = features.get('supply_to_borrow_ratio', 0)
        
        if ratio == 0:
            return 0  # No borrowing activity
        elif ratio <= 0.3:
            return 100  # Very low risk
        elif ratio <= 0.5:
            return 50   # Low risk
        elif ratio <= 0.7:
            return 0    # Moderate risk
        elif ratio <= 0.9:
            return -50  # High risk
        else:
            return -100 # Very high risk
    
    def _score_liquidation_count(self, features: Dict) -> float:
        """
        Score based on liquidation history
        Fewer liquidations = lower risk = higher score
        """
        liquidations = features.get('number_of_liquidations', 0)
        
        if liquidations == 0:
            return 50   # No liquidations
        elif liquidations == 1:
            return -25  # One liquidation
        elif liquidations == 2:
            return -50  # Two liquidations
        elif liquidations <= 5:
            return -75  # Multiple liquidations
        else:
            return -100 # Many liquidations
    
    def _score_inactivity_days(self, features: Dict) -> float:
        """
        Score based on days since last activity
        Recent activity = lower risk = higher score
        """
        inactivity_days = features.get('days_since_last_activity', 365)
        
        if inactivity_days <= 7:
            return 50   # Very recent activity
        elif inactivity_days <= 30:
            return 25   # Recent activity
        elif inactivity_days <= 90:
            return 0    # Moderate inactivity
        elif inactivity_days <= 180:
            return -25  # Long inactivity
        else:
            return -50  # Very long inactivity
    
    def _score_repayment_frequency(self, features: Dict) -> float:
        """
        Score based on repayment frequency
        Higher frequency = lower risk = higher score
        """
        frequency = features.get('repayment_frequency', 0)
        
        if frequency >= 2.0:
            return 50   # Very frequent repayments
        elif frequency >= 1.0:
            return 25   # Frequent repayments
        elif frequency >= 0.5:
            return 0    # Moderate repayments
        elif frequency > 0:
            return -25  # Infrequent repayments
        else:
            return -50  # No repayments
    
    def _score_volatile_asset_usage(self, features: Dict) -> float:
        """
        Score based on volatile asset usage
        Lower usage = lower risk = higher score
        """
        volatile_usage = features.get('volatile_asset_usage', 0)
        
        if volatile_usage <= 0.1:
            return 50   # Very low volatile asset usage
        elif volatile_usage <= 0.3:
            return 25   # Low volatile asset usage
        elif volatile_usage <= 0.5:
            return 0    # Moderate volatile asset usage
        elif volatile_usage <= 0.7:
            return -25  # High volatile asset usage
        else:
            return -50  # Very high volatile asset usage
    
    def _score_protocol_version(self, features: Dict) -> float:
        """
        Score based on protocol version usage
        V3 = lower risk = higher score
        """
        version = features.get('protocol_version_usage', 'none')
        
        if version == 'v3':
            return 25   # V3 is newer and generally safer
        elif version == 'v2':
            return 0    # V2 is stable but older
        elif version == 'none':
            return -25  # No protocol usage
        else:
            return 0    # Unknown version
    
    def _score_collateral_factor(self, features: Dict) -> float:
        """
        Score based on average collateral factor
        Higher factor = lower risk = higher score
        """
        collateral_factor = features.get('collateral_factor_average', 0)
        
        if collateral_factor >= 0.8:
            return 25   # High collateral factor
        elif collateral_factor >= 0.6:
            return 0    # Moderate collateral factor
        elif collateral_factor >= 0.4:
            return -25  # Low collateral factor
        else:
            return -50  # Very low collateral factor
    
    def score_all_wallets(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate risk scores for all wallets
        """
        scores = []
        
        for _, row in features_df.iterrows():
            features = row.to_dict()
            score = self.calculate_risk_score(features)
            
            scores.append({
                'wallet_id': features['wallet_id'],
                'score': score
            })
        
        return pd.DataFrame(scores)
    
    def normalize_scores(self, scores_df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize scores using min-max scaling to ensure 0-1000 range
        """
        if scores_df.empty:
            return scores_df
        
        # Extract scores for normalization
        scores = scores_df['score'].values.reshape(-1, 1)
        
        # Apply min-max scaling to 0-1000 range
        normalized_scores = self.scaler.fit_transform(scores) * 1000
        
        # Update the dataframe
        scores_df['score'] = normalized_scores.astype(int)
        
        return scores_df
    
    def get_risk_category(self, score: int) -> str:
        """
        Categorize risk based on score
        """
        if score >= 800:
            return 'Very Low Risk'
        elif score >= 600:
            return 'Low Risk'
        elif score >= 400:
            return 'Moderate Risk'
        elif score >= 200:
            return 'High Risk'
        else:
            return 'Very High Risk'
    
    def generate_risk_summary(self, scores_df: pd.DataFrame) -> Dict:
        """
        Generate summary statistics for risk scores
        """
        if scores_df.empty:
            return {}
        
        scores = scores_df['score'].values
        
        summary = {
            'total_wallets': len(scores),
            'average_score': np.mean(scores),
            'median_score': np.median(scores),
            'std_score': np.std(scores),
            'min_score': np.min(scores),
            'max_score': np.max(scores),
            'risk_distribution': {
                'Very Low Risk': len(scores[scores >= 800]),
                'Low Risk': len(scores[(scores >= 600) & (scores < 800)]),
                'Moderate Risk': len(scores[(scores >= 400) & (scores < 600)]),
                'High Risk': len(scores[(scores >= 200) & (scores < 400)]),
                'Very High Risk': len(scores[scores < 200])
            }
        }
        
        return summary 