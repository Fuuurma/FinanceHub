from typing import Dict, List
import math


class RiskManagementService:
    """Risk management and position sizing service."""
    
    MAX_POSITION_PERCENTAGE = 0.20
    MAX_RISK_PER_TRADE = 0.02
    
    def calculate_position_size(
        self,
        portfolio_value: float,
        account_balance: float,
        risk_per_trade: float,
        entry_price: float,
        stop_loss_price: float
    ) -> Dict:
        """Calculate optimal position size using fixed fractional method."""
        if portfolio_value <= 0:
            return {'error': 'Portfolio value must be positive'}
        if account_balance <= 0:
            return {'error': 'Account balance must be positive'}
        if risk_per_trade <= 0:
            return {'error': 'Risk per trade must be positive'}
        if entry_price <= 0:
            return {'error': 'Entry price must be positive'}
        if stop_loss_price <= 0:
            return {'error': 'Stop loss price must be positive'}
        
        risk_per_share = abs(entry_price - stop_loss_price)
        if risk_per_share == 0:
            return {'error': 'Entry price and stop loss cannot be the same'}
        
        risk_amount = account_balance * risk_per_trade
        position_shares = risk_amount / risk_per_share
        position_value = position_shares * entry_price
        position_pct = (position_value / portfolio_value) if portfolio_value > 0 else 0
        
        max_loss = position_shares * risk_per_share
        
        return {
            'position_shares': round(position_shares, 2),
            'position_value': round(position_value, 2),
            'position_percentage': round(position_pct * 100, 2),
            'risk_amount': round(risk_amount, 2),
            'risk_per_share': round(risk_per_share, 2),
            'max_loss': round(max_loss, 2),
            'stop_loss_distance': round(risk_per_share / entry_price * 100, 2)
        }
    
    def calculate_stop_loss(
        self,
        entry_price: float,
        stop_loss_pct: float,
        position_type: str = 'LONG'
    ) -> Dict:
        """Calculate stop loss price."""
        if entry_price <= 0:
            return {'error': 'Entry price must be positive'}
        if stop_loss_pct <= 0:
            return {'error': 'Stop loss percentage must be positive'}
        
        if position_type == 'LONG':
            stop_loss_price = entry_price * (1 - stop_loss_pct)
        else:
            stop_loss_price = entry_price * (1 + stop_loss_pct)
        
        return {
            'stop_loss_price': round(stop_loss_price, 2),
            'stop_loss_pct': round(stop_loss_pct * 100, 2),
            'position_type': position_type
        }
    
    def calculate_risk_reward_ratio(
        self,
        entry_price: float,
        stop_loss: float,
        target_price: float
    ) -> Dict:
        """Calculate risk/reward ratio."""
        if entry_price <= 0:
            return {'error': 'Entry price must be positive'}
        if stop_loss <= 0:
            return {'error': 'Stop loss must be positive'}
        if target_price <= 0:
            return {'error': 'Target price must be positive'}
        
        risk = abs(entry_price - stop_loss)
        reward = abs(target_price - entry_price)
        
        if risk == 0:
            return {'error': 'Risk cannot be zero'}
        
        ratio = reward / risk
        
        if ratio >= 3.0:
            verdict = 'EXCELLENT'
            color = 'green'
        elif ratio >= 2.0:
            verdict = 'GOOD'
            color = 'blue'
        elif ratio >= 1.0:
            verdict = 'FAIR'
            color = 'yellow'
        else:
            verdict = 'POOR'
            color = 'red'
        
        return {
            'risk_reward_ratio': round(ratio, 2),
            'verdict': verdict,
            'color': color,
            'risk_per_share': round(risk, 2),
            'reward_per_share': round(reward, 2)
        }
    
    def calculate_portfolio_risk_score(
        self,
        positions: List[Dict]
    ) -> Dict:
        """Calculate overall portfolio risk score."""
        if not positions:
            return {'risk_score': 0, 'risk_level': 'NONE', 'factors': []}
        
        total_value = sum(p.get('value', 0) for p in positions)
        if total_value <= 0:
            return {'error': 'Portfolio value must be positive'}
        
        risk_factors = []
        risk_score = 0
        
        max_position_pct = max((p.get('value', 0) / total_value * 100) for p in positions)
        if max_position_pct > 20:
            risk_score += 20
            risk_factors.append({
                'type': 'CONCENTRATION',
                'severity': 'HIGH',
                'description': f'Max position is {max_position_pct:.1f}% (>20% recommended)'
            })
        elif max_position_pct > 10:
            risk_score += 10
            risk_factors.append({
                'type': 'CONCENTRATION',
                'severity': 'MEDIUM',
                'description': f'Max position is {max_position_pct:.1f}%'
            })
        
        avg_volatility = sum(p.get('volatility', 0.2) for p in positions) / len(positions)
        if avg_volatility > 0.4:
            risk_score += 20
            risk_factors.append({
                'type': 'VOLATILITY',
                'severity': 'HIGH',
                'description': f'High volatility: {avg_volatility:.1%}'
            })
        elif avg_volatility > 0.25:
            risk_score += 10
            risk_factors.append({
                'type': 'VOLATILITY',
                'severity': 'MEDIUM',
                'description': f'Moderate volatility: {avg_volatility:.1%}'
            })
        
        if risk_score >= 50:
            risk_level = 'VERY HIGH'
        elif risk_score >= 30:
            risk_level = 'HIGH'
        elif risk_score >= 15:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'factors': risk_factors
        }
