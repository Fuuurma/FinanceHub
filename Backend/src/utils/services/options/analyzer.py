"""
Options Analyzer Service
Options pricing and Greeks with interpretable insights.

Philosophy:
- Greeks tell a story about option behavior
- Each option has a personality - Delta, Theta, Vega explain it
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import numpy as np
from scipy.stats import norm

from utils.helpers.logger.logger import get_logger
from utils.services.options_greeks import OptionsGreeksCalculator
from utils.constants.analytics import (
    DEFAULT_RISK_FREE_RATE,
    DEFAULT_OPTION_EXPIRATION_MONTHS,
    MAX_STRIKES_FOR_CHAIN,
)

logger = get_logger(__name__)


@dataclass
class OptionAnalysisReport:
    """
    Complete option analysis with Greeks and interpretation.
    
    What it represents:
    Full option pricing and risk analysis.
    
    Interpretation:
    - "This call has 60% probability of expiring in-the-money"
    - "Theta of -0.05 means option loses $0.05 per day from time decay"
    """
    underlying_price: float
    strike_price: float
    time_to_expiration: float
    volatility: float
    risk_free_rate: float
    option_type: str
    fair_price: float
    greeks: Dict[str, float]
    probability_itm: float
    breakeven: float
    interpretation: str
    fetched_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class VolSurfaceReport:
    """
    Volatility surface analysis.
    
    What it represents:
    How implied volatility varies by strike and expiration.
    
    Interpretation:
    - "40-strike puts have 5% more IV than ATM - traders buying protection"
    - "Skew of 0.15 indicates significant downside premium"
    """
    underlying_symbol: str
    strikes: List[float]
    expirations: List[float]
    implied_vols: Dict[Tuple[float, float], float]
    atm_vol: float
    vol_skew: float
    skew_direction: str
    interpretation: str
    fetched_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class OptionsChainReport:
    """
    Options chain analysis.
    
    What it represents:
    Greeks and analysis for entire options chain.
    
    Interpretation:
    - "Put/Call ratio of 0.8 suggests slight bullish sentiment"
    - "Max pain at $175 - most options expire worthless at this strike"
    """
    underlying_symbol: str
    underlying_price: float
    time_to_expiration: float
    option_type: str
    strikes: List[float]
    greeks_by_strike: Dict[float, Dict[str, float]]
    put_call_ratio: Optional[float]
    max_pain: Optional[float]
    interpretation: str
    fetched_at: str = field(default_factory=lambda: datetime.now().isoformat())


class OptionsAnalyzer:
    """
    Options pricing and Greeks with interpretable insights.
    
    Usage:
        analyzer = OptionsAnalyzer()
        
        # Single option analysis
        report = analyzer.analyze_option(
            S=175, K=180, T=0.25, r=0.05, sigma=0.2, option_type="call"
        )
        
        # Options chain
        chain = analyzer.analyze_options_chain(
            underlying_price=175,
            strikes=[170, 175, 180, 185, 190],
            T=0.25, r=0.05, iv_map={}
        )
    """
    
    def analyze_option(
        self,
        S: float,
        K: float,
        T: float,
        r: float = DEFAULT_RISK_FREE_RATE,
        sigma: float = 0.2,
        option_type: str = "call"
    ) -> OptionAnalysisReport:
        """
        Full option analysis with Greeks and interpretation.
        
        Args:
            S: Underlying price
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free rate
            sigma: Volatility
            option_type: "call" or "put"
        
        Returns:
            OptionAnalysisReport with all metrics and interpretation
        """
        if T <= 0 or sigma <= 0:
            return self._empty_option_report(S, K, T, option_type)
        
        try:
            greeks = OptionsGreeksCalculator.calculate_greeks(S, K, T, r, sigma, option_type)
            fair_price = OptionsGreeksCalculator.calculate_option_price(S, K, T, r, sigma, option_type)
            
            d1 = greeks['d1']
            prob_itm = norm.cdf(d1) if option_type == "call" else norm.cdf(-d1)
            
            breakeven = K + fair_price if option_type == "call" else K - fair_price
            
            interpretation = self._generate_option_interpretation(
                S, K, fair_price, greeks, prob_itm, option_type
            )
            
            return OptionAnalysisReport(
                underlying_price=S,
                strike_price=K,
                time_to_expiration=T,
                volatility=sigma,
                risk_free_rate=r,
                option_type=option_type,
                fair_price=fair_price,
                greeks={
                    'delta': greeks['delta'],
                    'gamma': greeks['gamma'],
                    'theta': greeks['theta'],
                    'vega': greeks['vega'],
                    'rho': greeks['rho'],
                },
                probability_itm=prob_itm,
                breakeven=breakeven,
                interpretation=interpretation,
            )
            
        except Exception as e:
            logger.error(f"Error analyzing option: {e}")
            return self._empty_option_report(S, K, T, option_type)
    
    def analyze_options_chain(
        self,
        underlying_price: float,
        strikes: List[float],
        T: float,
        r: float = DEFAULT_RISK_FREE_RATE,
        iv_map: Optional[Dict[float, float]] = None,
        option_type: str = "call"
    ) -> OptionsChainReport:
        """
        Analyze entire options chain.
        
        Args:
            underlying_price: Current underlying price
            strikes: List of strike prices
            T: Time to expiration (years)
            r: Risk-free rate
            iv_map: Optional strike -> IV mapping
            option_type: "call" or "put"
        
        Returns:
            OptionsChainReport with Greeks by strike
        """
        if len(strikes) > MAX_STRIKES_FOR_CHAIN:
            strikes = strikes[:MAX_STRIKES_FOR_CHAIN]
        
        greeks_by_strike = {}
        for strike in strikes:
            sigma = iv_map.get(strike, 0.2) if iv_map else 0.2
            greeks = OptionsGreeksCalculator.calculate_greeks(
                underlying_price, strike, T, r, sigma, option_type
            )
            price = OptionsGreeksCalculator.calculate_option_price(
                underlying_price, strike, T, r, sigma, option_type
            )
            greeks_by_strike[strike] = {
                'price': price,
                'delta': greeks['delta'],
                'gamma': greeks['gamma'],
                'theta': greeks['theta'],
                'vega': greeks['vega'],
            }
        
        put_call_ratio = None
        max_pain = None
        
        interpretation = self._generate_chain_interpretation(
            underlying_price, strikes, greeks_by_strike
        )
        
        return OptionsChainReport(
            underlying_symbol="",
            underlying_price=underlying_price,
            time_to_expiration=T,
            option_type=option_type,
            strikes=strikes,
            greeks_by_strike=greeks_by_strike,
            put_call_ratio=put_call_ratio,
            max_pain=max_pain,
            interpretation=interpretation,
        )
    
    def analyze_vol_surface(
        self,
        underlying_symbol: str,
        strikes: List[float],
        expirations: List[float],
        iv_data: Dict[Tuple[float, float], float],
        underlying_price: float
    ) -> VolSurfaceReport:
        """
        Analyze volatility surface.
        
        Args:
            underlying_symbol: Asset symbol
            strikes: Available strikes
            expirations: Available expirations
            iv_data: Dict of (strike, expiration) -> IV
            underlying_price: Current price
            
        Returns:
            VolSurfaceReport with skew analysis
        """
        atm_key = None
        for exp in expirations:
            for strike in strikes:
                if abs(strike - underlying_price) < 0.05 * underlying_price:
                    atm_key = (strike, exp)
                    break
        
        atm_vol = iv_data.get(atm_key, 0.2) if atm_key else 0.2
        
        skew_values = []
        for (strike, exp), iv in iv_data.items():
            if strike < underlying_price:
                skew_values.append(iv - atm_vol)
        
        vol_skew = np.mean(skew_values) if skew_values else 0
        skew_direction = "put_skew" if vol_skew > 0.02 else "call_skew" if vol_skew < -0.02 else "symmetric"
        
        interpretation = self._generate_vol_surface_interpretation(
            atm_vol, vol_skew, skew_direction
        )
        
        return VolSurfaceReport(
            underlying_symbol=underlying_symbol,
            strikes=strikes,
            expirations=expirations,
            implied_vols=iv_data,
            atm_vol=atm_vol,
            vol_skew=vol_skew,
            skew_direction=skew_direction,
            interpretation=interpretation,
        )
    
    def _generate_option_interpretation(
        self,
        S: float,
        K: float,
        price: float,
        greeks: Dict,
        prob_itm: float,
        option_type: str
    ) -> str:
        """Generate option interpretation."""
        if option_type == "call":
            interp = f"CALL at ${K:.2f} on ${S:.2f} underlying:"
            interp += f"\n• Fair value: ${price:.2f}"
            interp += f"\n• Probability ITM: {prob_itm*100:.0f}%"
            interp += f"\n• Delta: {greeks['delta']:.3f} (price change per $1 move)"
            
            delta = greeks['delta']
            if delta > 0.7:
                interp += " - Deep ITM, high correlation to stock"
            elif delta > 0.4:
                interp += " - Moderate ITM, reasonable leverage"
            elif delta > 0.2:
                interp += " - OTM, low probability but high reward"
            else:
                interp += " - Deep OTM, lottery ticket territory"
            
            interp += f"\n• Theta: {greeks['theta']:.3f} (daily time decay)"
            if greeks['theta'] < -0.1:
                interp += " - High time decay, avoid holding"
            elif greeks['theta'] > -0.02:
                interp += " - Low time decay, suitable for holding"
            
            interp += f"\n• Gamma: {greeks['gamma']:.4f} (acceleration of delta)"
            
        else:
            interp = f"PUT at ${K:.2f} on ${S:.2f} underlying:"
            interp += f"\n• Fair value: ${price:.2f}"
            interp += f"\n• Probability ITM: {(1-prob_itm)*100:.0f}%"
            interp += f"\n• Delta: {greeks['delta']:.3f}"
            
            delta = abs(greeks['delta'])
            if delta > 0.7:
                interp += " - Deep ITM, like owning stock with protection"
            elif delta > 0.4:
                interp += " - Moderate ITM, reasonable hedge"
            elif delta > 0.2:
                interp += " - OTM, speculation on downside"
            else:
                interp += " - Deep OTM, cheap protection"
            
            interp += f"\n• Theta: {greeks['theta']:.3f}"
            interp += f"\n• Gamma: {greeks['gamma']:.4f}"
        
        interp += f"\n• Vega: {greeks['vega']:.3f} (IV sensitivity)"
        
        return interp
    
    def _generate_chain_interpretation(
        self,
        underlying: float,
        strikes: List[float],
        greeks: Dict[float, Dict]
    ) -> str:
        """Generate options chain interpretation."""
        interp = f"Options chain for ${underlying:.2f}: {len(strikes)} strikes analyzed"
        
        atm_strike = min(strikes, key=lambda x: abs(x - underlying))
        if atm_strike in greeks:
            atm = greeks[atm_strike]
            interp += f"\n• ATM ({atm_strike}): Delta {atm['delta']:.3f}, Theta {atm['theta']:.3f}"
        
        if len(strikes) >= 3:
            low_strike = min(strikes)
            high_strike = max(strikes)
            if low_strike in greeks and high_strike in greeks:
                interp += f"\n• OTM call (${high_strike}): Delta {greeks[high_strike]['delta']:.3f}"
                interp += f"\n• OTM put (${low_strike}): Delta {greeks[low_strike]['delta']:.3f}"
        
        return interp
    
    def _generate_vol_surface_interpretation(
        self,
        atm_vol: float,
        vol_skew: float,
        skew_direction: str
    ) -> str:
        """Generate vol surface interpretation."""
        interp = f"ATM volatility: {atm_vol*100:.1f}%"
        
        if skew_direction == "put_skew":
            interp += " - Put skew present (downside protection demand)"
        elif skew_direction == "call_skew":
            interp += " - Call skew present (upside speculation)"
        else:
            interp += " - Symmetric vol surface"
        
        if abs(vol_skew) > 0.02:
            interp += f", skew magnitude: {abs(vol_skew)*100:.1f}%"
        
        return interp
    
    def _empty_option_report(
        self, S: float, K: float, T: float, option_type: str
    ) -> OptionAnalysisReport:
        """Return empty option report."""
        return OptionAnalysisReport(
            underlying_price=S,
            strike_price=K,
            time_to_expiration=T,
            volatility=0,
            risk_free_rate=0,
            option_type=option_type,
            fair_price=0,
            greeks={'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0, 'rho': 0},
            probability_itm=0,
            breakeven=0,
            interpretation="Invalid option parameters",
        )
