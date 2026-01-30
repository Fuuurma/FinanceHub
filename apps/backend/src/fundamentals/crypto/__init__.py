"""
Crypto fundamental data models.
Contains TVL, protocol revenue, staking, and supply metrics.
"""

from .protocol_metrics import CryptoProtocolMetrics, StakingData, CryptoSupplyMetrics

__all__ = [
    "CryptoProtocolMetrics",
    "StakingData",
    "CryptoSupplyMetrics",
]
