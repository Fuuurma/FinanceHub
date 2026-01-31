"""
Tests for RiskManagementService
Tests position sizing, stop loss, risk/reward ratio, and portfolio risk scoring.
"""

import pytest
from investments.services.risk_service import RiskManagementService


class TestRiskManagementService:
    """Test cases for RiskManagementService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = RiskManagementService()
    
    def test_calculate_position_size_basic(self):
        """Test basic position size calculation."""
        result = self.service.calculate_position_size(
            portfolio_value=100000,
            account_balance=50000,
            risk_per_trade=0.01,
            entry_price=150,
            stop_loss_price=142.5
        )
        
        assert result['position_shares'] == 333.33
        assert result['position_value'] == 50000
        assert result['position_percentage'] == 50.0
        assert result['risk_amount'] == 500
        assert result['risk_per_share'] == 7.5
        assert result['max_loss'] == 2500
        assert result['stop_loss_distance'] == 5.0
    
    def test_calculate_position_size_long_position(self):
        """Test position size for long position."""
        result = self.service.calculate_position_size(
            portfolio_value=100000,
            account_balance=100000,
            risk_per_trade=0.02,
            entry_price=100,
            stop_loss_price=95
        )
        
        assert result['position_shares'] == 400
        assert result['position_value'] == 40000
        assert result['risk_amount'] == 2000
        assert result['risk_per_share'] == 5
    
    def test_calculate_position_size_short_position(self):
        """Test position size for short position."""
        result = self.service.calculate_position_size(
            portfolio_value=100000,
            account_balance=100000,
            risk_per_trade=0.01,
            entry_price=100,
            stop_loss_price=105
        )
        
        assert result['position_shares'] == 200
        assert result['position_value'] == 20000
        assert result['risk_per_share'] == 5
    
    def test_calculate_position_size_invalid_zero_risk(self):
        """Test position size with zero risk (entry = stop loss)."""
        result = self.service.calculate_position_size(
            portfolio_value=100000,
            account_balance=50000,
            risk_per_trade=0.01,
            entry_price=150,
            stop_loss_price=150
        )
        
        assert 'error' in result
        assert 'same' in result['error']
    
    def test_calculate_position_size_invalid_negative_prices(self):
        """Test position size with negative prices."""
        result = self.service.calculate_position_size(
            portfolio_value=100000,
            account_balance=50000,
            risk_per_trade=0.01,
            entry_price=-100,
            stop_loss_price=90
        )
        
        assert 'error' in result
        assert 'positive' in result['error']
    
    def test_calculate_position_size_invalid_zero_balance(self):
        """Test position size with zero account balance."""
        result = self.service.calculate_position_size(
            portfolio_value=100000,
            account_balance=0,
            risk_per_trade=0.01,
            entry_price=150,
            stop_loss_price=142.5
        )
        
        assert 'error' in result
        assert 'positive' in result['error']
    
    def test_calculate_stop_loss_long(self):
        """Test stop loss calculation for long position."""
        result = self.service.calculate_stop_loss(
            entry_price=100,
            stop_loss_pct=0.05,
            position_type='LONG'
        )
        
        assert result['stop_loss_price'] == 95
        assert result['stop_loss_pct'] == 5.0
        assert result['position_type'] == 'LONG'
    
    def test_calculate_stop_loss_short(self):
        """Test stop loss calculation for short position."""
        result = self.service.calculate_stop_loss(
            entry_price=100,
            stop_loss_pct=0.05,
            position_type='SHORT'
        )
        
        assert result['stop_loss_price'] == 105
        assert result['stop_loss_pct'] == 5.0
        assert result['position_type'] == 'SHORT'
    
    def test_calculate_stop_loss_default_long(self):
        """Test default position type is LONG."""
        result = self.service.calculate_stop_loss(
            entry_price=100,
            stop_loss_pct=0.05
        )
        
        assert result['position_type'] == 'LONG'
        assert result['stop_loss_price'] == 95
    
    def test_calculate_stop_loss_invalid_negative_price(self):
        """Test stop loss with negative entry price."""
        result = self.service.calculate_stop_loss(
            entry_price=-100,
            stop_loss_pct=0.05
        )
        
        assert 'error' in result
    
    def test_calculate_risk_reward_ratio_excellent(self):
        """Test risk/reward ratio - excellent (3:1 or better)."""
        result = self.service.calculate_risk_reward_ratio(
            entry_price=100,
            stop_loss=90,
            target_price=130
        )
        
        assert result['risk_reward_ratio'] == 3.0
        assert result['verdict'] == 'EXCELLENT'
        assert result['color'] == 'green'
        assert result['risk_per_share'] == 10
        assert result['reward_per_share'] == 30
    
    def test_calculate_risk_reward_ratio_good(self):
        """Test risk/reward ratio - good (2:1)."""
        result = self.service.calculate_risk_reward_ratio(
            entry_price=100,
            stop_loss=90,
            target_price=120
        )
        
        assert result['risk_reward_ratio'] == 2.0
        assert result['verdict'] == 'GOOD'
        assert result['color'] == 'blue'
    
    def test_calculate_risk_reward_ratio_fair(self):
        """Test risk/reward ratio - fair (1.5:1)."""
        result = self.service.calculate_risk_reward_ratio(
            entry_price=100,
            stop_loss=90,
            target_price=115
        )
        
        assert result['risk_reward_ratio'] == 1.5
        assert result['verdict'] == 'FAIR'
        assert result['color'] == 'yellow'
    
    def test_calculate_risk_reward_ratio_poor(self):
        """Test risk/reward ratio - poor (0.5:1)."""
        result = self.service.calculate_risk_reward_ratio(
            entry_price=100,
            stop_loss=90,
            target_price=105
        )
        
        assert result['risk_reward_ratio'] == 0.5
        assert result['verdict'] == 'POOR'
        assert result['color'] == 'red'
    
    def test_calculate_risk_reward_ratio_invalid_zero_risk(self):
        """Test risk/reward with zero risk."""
        result = self.service.calculate_risk_reward_ratio(
            entry_price=100,
            stop_loss=100,
            target_price=130
        )
        
        assert 'error' in result
    
    def test_calculate_portfolio_risk_score_low_risk(self):
        """Test portfolio risk score - low risk portfolio."""
        positions = [
            {'symbol': 'AAPL', 'value': 10000, 'volatility': 0.2},
            {'symbol': 'GOOGL', 'value': 10000, 'volatility': 0.2},
            {'symbol': 'MSFT', 'value': 10000, 'volatility': 0.2},
        ]
        
        result = self.service.calculate_portfolio_risk_score(positions)
        
        assert result['risk_score'] == 0
        assert result['risk_level'] == 'LOW'
        assert len(result['factors']) == 0
    
    def test_calculate_portfolio_risk_score_high_concentration(self):
        """Test portfolio risk score - high concentration."""
        positions = [
            {'symbol': 'AAPL', 'value': 50000, 'volatility': 0.2},
            {'symbol': 'GOOGL', 'value': 10000, 'volatility': 0.2},
        ]
        
        result = self.service.calculate_portfolio_risk_score(positions)
        
        assert result['risk_score'] == 20
        assert result['risk_level'] == 'HIGH'
        assert len(result['factors']) > 0
        assert any(f['type'] == 'CONCENTRATION' for f in result['factors'])
    
    def test_calculate_portfolio_risk_score_high_volatility(self):
        """Test portfolio risk score - high volatility portfolio."""
        positions = [
            {'symbol': 'BTC', 'value': 10000, 'volatility': 0.6},
            {'symbol': 'ETH', 'value': 10000, 'volatility': 0.5},
            {'symbol': 'SOL', 'value': 10000, 'volatility': 0.55},
        ]
        
        result = self.service.calculate_portfolio_risk_score(positions)
        
        assert result['risk_score'] >= 20
        assert len(result['factors']) > 0
        assert any(f['type'] == 'VOLATILITY' for f in result['factors'])
    
    def test_calculate_portfolio_risk_score_empty(self):
        """Test portfolio risk score with empty positions."""
        result = self.service.calculate_portfolio_risk_score([])
        
        assert result['risk_score'] == 0
        assert result['risk_level'] == 'NONE'
        assert len(result['factors']) == 0
    
    def test_calculate_portfolio_risk_score_medium_concentration(self):
        """Test portfolio risk score - medium concentration (10-20%)."""
        positions = [
            {'symbol': 'AAPL', 'value': 15000, 'volatility': 0.2},
            {'symbol': 'GOOGL', 'value': 10000, 'volatility': 0.2},
            {'symbol': 'MSFT', 'value': 10000, 'volatility': 0.2},
        ]
        
        result = self.service.calculate_portfolio_risk_score(positions)
        
        assert result['risk_score'] == 10
        assert result['risk_level'] == 'MEDIUM'
        assert len(result['factors']) > 0
    
    def test_calculate_portfolio_risk_score_very_high_risk(self):
        """Test portfolio risk score - very high risk."""
        positions = [
            {'symbol': 'TSLA', 'value': 80000, 'volatility': 0.6},
            {'symbol': 'NVDA', 'value': 60000, 'volatility': 0.5},
        ]
        
        result = self.service.calculate_portfolio_risk_score(positions)
        
        assert result['risk_score'] >= 50
        assert result['risk_level'] in ['HIGH', 'VERY HIGH']


class TestPositionSizeFormulas:
    """Test specific formulas for position sizing."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = RiskManagementService()
    
    def test_position_size_formula(self):
        """Test the core position size formula."""
        result = self.service.calculate_position_size(
            portfolio_value=100000,
            account_balance=100000,
            risk_per_trade=0.01,
            entry_price=100,
            stop_loss_price=95
        )
        
        risk_amount = 100000 * 0.01
        risk_per_share = 5
        expected_shares = risk_amount / risk_per_share
        
        assert result['position_shares'] == expected_shares
    
    def test_position_value_calculation(self):
        """Test position value = shares * entry price."""
        result = self.service.calculate_position_size(
            portfolio_value=100000,
            account_balance=50000,
            risk_per_trade=0.01,
            entry_price=100,
            stop_loss_price=95
        )
        
        expected_value = result['position_shares'] * 100
        assert result['position_value'] == expected_value
    
    def test_max_loss_calculation(self):
        """Test max loss = shares * risk per share."""
        result = self.service.calculate_position_size(
            portfolio_value=100000,
            account_balance=50000,
            risk_per_trade=0.02,
            entry_price=100,
            stop_loss_price=90
        )
        
        expected_max_loss = result['position_shares'] * 10
        assert result['max_loss'] == expected_max_loss


class TestStopLossCalculations:
    """Test stop loss calculation edge cases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = RiskManagementService()
    
    def test_stop_loss_small_percentage(self):
        """Test stop loss with small percentage."""
        result = self.service.calculate_stop_loss(
            entry_price=100,
            stop_loss_pct=0.01,
            position_type='LONG'
        )
        
        assert result['stop_loss_price'] == 99
    
    def test_stop_loss_large_percentage(self):
        """Test stop loss with larger percentage."""
        result = self.service.calculate_stop_loss(
            entry_price=100,
            stop_loss_pct=0.10,
            position_type='LONG'
        )
        
        assert result['stop_loss_price'] == 90
    
    def test_stop_loss_short_inverse(self):
        """Test short stop loss is above entry."""
        result = self.service.calculate_stop_loss(
            entry_price=100,
            stop_loss_pct=0.05,
            position_type='SHORT'
        )
        
        assert result['stop_loss_price'] > 100


class TestRiskRewardEdgeCases:
    """Test edge cases for risk/reward calculations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = RiskManagementService()
    
    def test_risk_reward_ratio_boundary_3(self):
        """Test R/R ratio at boundary 3.0."""
        result = self.service.calculate_risk_reward_ratio(
            entry_price=100,
            stop_loss=90,
            target_price=130
        )
        
        assert result['risk_reward_ratio'] == 3.0
        assert result['verdict'] == 'EXCELLENT'
    
    def test_risk_reward_ratio_boundary_2(self):
        """Test R/R ratio at boundary 2.0."""
        result = self.service.calculate_risk_reward_ratio(
            entry_price=100,
            stop_loss=90,
            target_price=120
        )
        
        assert result['risk_reward_ratio'] == 2.0
        assert result['verdict'] == 'GOOD'
    
    def test_risk_reward_ratio_boundary_1(self):
        """Test R/R ratio at boundary 1.0."""
        result = self.service.calculate_risk_reward_ratio(
            entry_price=100,
            stop_loss=90,
            target_price=110
        )
        
        assert result['risk_reward_ratio'] == 1.0
        assert result['verdict'] == 'FAIR'
    
    def test_risk_reward_negative_prices(self):
        """Test R/R with negative prices returns error."""
        result = self.service.calculate_risk_reward_ratio(
            entry_price=-100,
            stop_loss=-90,
            target_price=-70
        )
        
        assert 'error' in result
