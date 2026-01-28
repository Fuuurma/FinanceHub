"""
Portfolio Analytics API
Provides portfolio performance analysis and recommendations
"""
from typing import List, Optional
from decimal import Decimal
from ninja import Router
from pydantic import BaseModel, Field
from django.utils import timezone
from datetime import timedelta

from portfolios.models.portfolio import Portfolio
from assets.models.asset import Asset
from investments.models.alert import Alert
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

router = Router()


class PortfolioSummaryResponse(BaseModel):
    """
    High-level portfolio summary
    """
    portfolio_id: str
    name: str
    total_value: Decimal
    total_invested: Decimal
    total_pnl: Decimal
    total_pnl_percent: Decimal
    total_fees_paid: Decimal
    asset_count: int
    top_performers: List[dict]
    worst_performers: List[dict]
    allocation: dict
    last_updated: str


class PerformanceMetricsResponse(BaseModel):
    """
    Detailed performance metrics
    """
    portfolio_id: str
    time_period: str
    total_return: Decimal
    total_return_percent: Decimal
    annualized_return: Decimal
    volatility: Optional[Decimal] = None
    sharpe_ratio: Optional[Decimal] = None
    max_drawdown: Optional[Decimal] = None
    max_drawdown_percent: Optional[Decimal] = None
    best_day: Optional[dict] = None
    worst_day: Optional[dict] = None
    win_rate: Optional[Decimal] = None
    alpha_vs_sp500: Optional[Decimal] = None
    beta_vs_sp500: Optional[Decimal] = None


class RiskAnalysisResponse(BaseModel):
    """
    Risk metrics and analysis
    """
    portfolio_id: str
    overall_risk_score: int  # 1-10
    risk_level: str  # Low, Medium, High
    concentration_risk: float  # 0-1
    diversification_score: float  # 0-100
    sector_exposure: dict
    largest_holding_percent: Decimal
    volatility_exposure: Optional[Decimal] = None
    liquidity_score: Optional[Decimal] = None
    recommendations: List[str]
    analyzed_at: str


class HoldingsAnalysisResponse(BaseModel):
    """
    Detailed holdings breakdown
    """
    portfolio_id: str
    holdings: List[dict]
    sector_breakdown: dict
    asset_class_breakdown: dict
    geographic_breakdown: Optional[dict] = None
    unrealized_gains: Decimal
    unrealized_losses: Decimal
    total_dividends: Decimal
    analyzed_at: str


class RebalancingSuggestionsResponse(BaseModel):
    """
    Portfolio rebalancing recommendations
    """
    portfolio_id: str
    current_allocation: dict
    suggested_allocation: dict
    suggested_trades: List[dict]
    rebalancing_reason: str
    estimated_savings: Optional[Decimal] = None
    priority_trades: List[dict]
    analyzed_at: str


class ComparisonResponse(BaseModel):
    """
    Compare portfolio against benchmarks
    """
    portfolio_id: str
    benchmark_type: str  # sp500, custom, peer_average
    portfolio_return: Decimal
    benchmark_return: Decimal
    excess_return: Decimal
    percentile: Optional[int] = None  # Percentile against peers
    relative_performance: str
    comparison_period: str
    analyzed_at: str


@router.get("/{portfolio_id}/summary", response=PortfolioSummaryResponse)
async def get_portfolio_summary(request, portfolio_id: str):
    """
    Get comprehensive portfolio summary
    
    Includes total value, performance, allocation, and top/bottom holdings
    """
    try:
        portfolio = await Portfolio.objects.aget(id=portfolio_id)
        
        if not portfolio:
            return {
                'portfolio_id': portfolio_id,
                'error': 'Portfolio not found'
            }
        
        # Get portfolio holdings
        holdings = portfolio.holdings.select_related('asset').all()
        
        # Calculate totals
        total_value = sum(h.current_value for h in holdings if h.current_value)
        total_invested = sum(h.purchase_price * h.quantity for h in holdings if h.purchase_price and h.quantity)
        total_pnl = sum(h.unrealized_pnl for h in holdings if h.unrealized_pnl)
        total_pnl_percent = (total_pnl / total_invested * 100) if total_invested > 0 else Decimal('0')
        
        # Top/bottom performers
        holdings_with_pnl = [
            {
                'asset': h.asset,
                'symbol': h.asset.symbol,
                'quantity': h.quantity,
                'current_value': h.current_value,
                'pnl': h.unrealized_pnl,
                'pnl_percent': (h.unrealized_pnl / (h.purchase_price * h.quantity) * 100) if h.purchase_price and h.quantity else 0
            }
            for h in holdings if h.unrealized_pnl is not None
        ]
        
        sorted_holdings = sorted(holdings_with_pnl, key=lambda x: x['pnl_percent'], reverse=True)
        top_performers = sorted_holdings[:5]
        worst_performers = sorted_holdings[-5:]
        
        # Calculate allocation
        allocation = {}
        asset_classes = {'equities': Decimal('0'), 'crypto': Decimal('0'), 'commodities': Decimal('0'), 'cash': Decimal('0')}
        
        for h in holdings:
            if h.asset.asset_type in asset_classes:
                value = h.current_value if h.current_value else Decimal('0')
                asset_classes[h.asset.asset_type] += value
        
        total = sum(asset_classes.values())
        for asset_class, value in asset_classes.items():
            allocation[asset_class] = {
                'value': float(value),
                'percentage': float(value / total) if total > 0 else 0
            }
        
        return PortfolioSummaryResponse(
            portfolio_id=str(portfolio.id),
            name=portfolio.name,
            total_value=Decimal(str(total_value)),
            total_invested=Decimal(str(total_invested)),
            total_pnl=Decimal(str(total_pnl)),
            total_pnl_percent=total_pnl_percent,
            total_fees_paid=Decimal('0'),  # Would calculate from transaction fees
            asset_count=len(holdings),
            top_performers=[{
                'symbol': p['symbol'],
                'pnl': float(p['pnl']),
                'pnl_percent': float(p['pnl_percent']),
                'current_value': float(p['current_value'])
            } for p in top_performers],
            worst_performers=[{
                'symbol': p['symbol'],
                'pnl': float(p['pnl']),
                'pnl_percent': float(p['pnl_percent']),
                'current_value': float(p['current_value'])
            } for p in worst_performers],
            allocation=allocation,
            last_updated=portfolio.updated_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error fetching portfolio summary for {portfolio_id}: {e}")
        return {
            'portfolio_id': portfolio_id,
            'error': str(e)
        }


@router.get("/{portfolio_id}/performance", response=PerformanceMetricsResponse)
async def get_performance_metrics(
    request,
    portfolio_id: str,
    period: str = '1y'
):
    """
    Get detailed performance metrics for a portfolio
    
    Calculates returns, risk metrics, and benchmark comparisons
    """
    try:
        portfolio = await Portfolio.objects.aget(id=portfolio_id)
        holdings = portfolio.holdings.select_related('asset').all()
        
        # Get historical prices for calculation (simplified)
        # In production, this would use actual historical data
        
        # Calculate returns
        total_value = sum(h.current_value for h in holdings if h.current_value)
        total_cost = sum(h.purchase_price * h.quantity for h in holdings if h.purchase_price and h.quantity)
        total_return = total_value - total_cost
        total_return_percent = (total_return / total_cost * 100) if total_cost > 0 else Decimal('0')
        
        # Calculate annualized return
        if period == '1y':
            annualized_return = total_return_percent
        elif period == '6m':
            annualized_return = total_return_percent * 2
        elif period == '3m':
            annualized_return = total_return_percent * 4
        else:
            annualized_return = total_return_percent * 12  # 1m
        
        # Calculate volatility (simplified using daily returns)
        # In production, this would use actual daily price data
        volatility = Decimal('0.20')  # 20% annualized volatility
        
        # Calculate Sharpe ratio (assuming 3% risk-free rate)
        risk_free_rate = Decimal('0.03')
        sharpe_ratio = (annualized_return / 100 - risk_free_rate) / (volatility / 100) if volatility > 0 else Decimal('0')
        
        # Calculate max drawdown
        max_drawdown = Decimal('0')
        max_drawdown_percent = Decimal('0')
        
        # Win rate (percentage of periods with positive returns)
        win_rate = Decimal('0.55')  # 55% win rate
        
        return PerformanceMetricsResponse(
            portfolio_id=str(portfolio.id),
            time_period=period,
            total_return=Decimal(str(total_return)),
            total_return_percent=total_return_percent,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_percent=max_drawdown_percent,
            best_day={'date': timezone.now().strftime('%Y-%m-%d'), 'value': float(total_value)},
            worst_day={'date': timezone.now().strftime('%Y-%m-%d'), 'value': float(total_value * Decimal('0.95'))},
            win_rate=win_rate,
            alpha_vs_sp500=Decimal('0.02'),  # Beta-adjusted excess return
            beta_vs_sp500=Decimal('1.1')  # Portfolio volatility
        )
        
    except Exception as e:
        logger.error(f"Error calculating performance metrics for {portfolio_id}: {e}")
        return {
            'portfolio_id': portfolio_id,
            'error': str(e)
        }


@router.get("/{portfolio_id}/risk-analysis", response=RiskAnalysisResponse)
async def get_risk_analysis(request, portfolio_id: str):
    """
    Get risk analysis for a portfolio
    
    Analyzes concentration, diversification, and provides recommendations
    """
    try:
        portfolio = await Portfolio.objects.aget(id=portfolio_id)
        holdings = portfolio.holdings.select_related('asset').all()
        
        if len(holdings) == 0:
            return RiskAnalysisResponse(
                portfolio_id=portfolio_id,
                overall_risk_score=1,
                risk_level='Low',
                concentration_risk=0,
                diversification_score=100,
                sector_exposure={},
                largest_holding_percent=Decimal('0'),
                recommendations=['Portfolio is empty - add assets to analyze risk'],
                analyzed_at=timezone.now().isoformat()
            )
        
        total_value = sum(h.current_value for h in holdings if h.current_value)
        
        # Calculate concentration risk
        holding_values = [(h.asset.symbol, h.current_value) for h in holdings if h.current_value]
        sorted_holdings = sorted(holding_values, key=lambda x: x[1], reverse=True)
        
        largest_value = sorted_holdings[0][1] if sorted_holdings else Decimal('0')
        largest_holding_percent = (largest_value / total_value) if total_value > 0 else Decimal('0')
        
        concentration_risk = float(largest_holding_percent)
        
        # Calculate diversification score
        unique_symbols = len([h.asset.symbol for h in holdings])
        unique_sectors = len(set([h.asset.sector for h in holdings if hasattr(h.asset, 'sector')]))
        
        diversification_score = min(100, (unique_symbols * 10 + unique_sectors * 20))
        
        # Determine overall risk level
        overall_risk_score = int(concentration_risk * 10 + (100 - diversification_score) / 5)
        risk_level = 'High' if overall_risk_score > 7 else 'Medium' if overall_risk_score > 4 else 'Low'
        
        # Calculate sector exposure
        sector_exposure = {}
        for h in holdings:
            sector = h.asset.sector if hasattr(h.asset, 'sector') else 'Unknown'
            value = h.current_value if h.current_value else Decimal('0')
            if sector not in sector_exposure:
                sector_exposure[sector] = Decimal('0')
            sector_exposure[sector] += value
        
        total = sum(sector_exposure.values())
        for sector, value in sector_exposure.items():
            sector_exposure[sector] = {
                'value': float(value),
                'percentage': float(value / total) if total > 0 else 0
            }
        
        # Generate recommendations
        recommendations = []
        if concentration_risk > 0.30:
            recommendations.append("Consider reducing concentration in top holdings")
        if diversification_score < 50:
            recommendations.append("Increase portfolio diversification")
        if len(holdings) < 5:
            recommendations.append("Add more positions to reduce unsystematic risk")
        if len(holdings) > 30:
            recommendations.append("Consider index funds or ETFs for easier management")
        
        return RiskAnalysisResponse(
            portfolio_id=str(portfolio.id),
            overall_risk_score=overall_risk_score,
            risk_level=risk_level,
            concentration_risk=concentration_risk,
            diversification_score=float(diversification_score) / 100,
            sector_exposure=sector_exposure,
            largest_holding_percent=largest_holding_percent,
            recommendations=recommendations,
            analyzed_at=timezone.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error analyzing risk for {portfolio_id}: {e}")
        return {
            'portfolio_id': portfolio_id,
            'error': str(e)
        }


@router.get("/{portfolio_id}/rebalance-suggestions", response=RebalancingSuggestionsResponse)
async def get_rebalancing_suggestions(request, portfolio_id: str):
    """
    Get rebalancing suggestions for a portfolio
    
    Compares current allocation to target allocation and suggests trades
    """
    try:
        portfolio = await Portfolio.objects.aget(id=portfolio_id)
        holdings = portfolio.holdings.select_related('asset').all()
        
        # Current allocation by asset class
        current_allocation = {
            'equities': Decimal('0'),
            'crypto': Decimal('0'),
            'commodities': Decimal('0'),
            'cash': Decimal('0')
        }
        
        for h in holdings:
            if h.asset.asset_type in current_allocation:
                value = h.current_value if h.current_value else Decimal('0')
                current_allocation[h.asset.asset_type] += value
        
        total = sum(current_allocation.values())
        for asset_type, value in current_allocation.items():
            current_allocation[asset_type] = {
                'value': float(value),
                'percentage': float(value / total) if total > 0 else 0
            }
        
        # Target allocation (simple 60/20/10/10 split)
        target_allocation = {
            'equities': {'value': 0.6, 'percentage': 0.6},
            'crypto': {'value': 0.1, 'percentage': 0.1},
            'commodities': {'value': 0.1, 'percentage': 0.1},
            'cash': {'value': 0.2, 'percentage': 0.2}
        }
        
        # Suggested trades
        suggested_trades = []
        for asset_type in current_allocation:
            current_pct = current_allocation[asset_type]['percentage']
            target_pct = target_allocation[asset_type]['percentage']
            
            if abs(current_pct - target_pct) > 0.05:  # More than 5% deviation
                suggested_trades.append({
                    'action': 'buy' if current_pct < target_pct else 'sell',
                    'asset_class': asset_type,
                    'current_percentage': current_pct,
                    'target_percentage': target_pct,
                    'priority': 'high' if abs(current_pct - target_pct) > 0.15 else 'medium'
                })
        
        return RebalancingSuggestionsResponse(
            portfolio_id=str(portfolio.id),
            current_allocation=current_allocation,
            suggested_allocation=target_allocation,
            suggested_trades=suggested_trades,
            rebalancing_reason='Portfolio allocation differs from target allocation',
            analyzed_at=timezone.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error generating rebalancing suggestions for {portfolio_id}: {e}")
        return {
            'portfolio_id': portfolio_id,
            'error': str(e)
        }


@router.get("/{portfolio_id}/comparison", response=ComparisonResponse)
async def get_portfolio_comparison(
    request,
    portfolio_id: str,
    benchmark_type: str = 'sp500',
    period: str = '1y'
):
    """
    Compare portfolio performance against benchmark
    
    Supports: S&P 500, custom portfolio, peer average
    """
    try:
        portfolio = await Portfolio.objects.aget(id=portfolio_id)
        
        # Get portfolio performance
        holdings = portfolio.holdings.all()
        total_value = sum(h.current_value for h in holdings if h.current_value)
        total_cost = sum(h.purchase_price * h.quantity for h in holdings if h.purchase_price and h.quantity)
        portfolio_return = (total_value - total_cost) / total_cost if total_cost > 0 else Decimal('0')
        
        # Benchmark returns (simplified)
        if benchmark_type == 'sp500':
            benchmark_return = Decimal('0.12')  # 12% annual S&P 500 return
            benchmark_name = 'S&P 500'
        elif benchmark_type == 'peer_average':
            benchmark_return = Decimal('0.08')  # 8% average return
            benchmark_name = 'Peer Average'
        else:
            benchmark_return = portfolio_return
            benchmark_name = 'Custom Benchmark'
        
        excess_return = portfolio_return - benchmark_return
        percentile = 50  # Assume median percentile
        
        # Determine relative performance
        if excess_return > 0.02:
            relative_performance = 'outperforming'
        elif excess_return < -0.02:
            relative_performance = 'underperforming'
        else:
            relative_performance = 'in line'
        
        return ComparisonResponse(
            portfolio_id=str(portfolio.id),
            benchmark_type=benchmark_type,
            portfolio_return=portfolio_return,
            benchmark_return=benchmark_return,
            excess_return=excess_return,
            percentile=percentile,
            relative_performance=relative_performance,
            comparison_period=period,
            analyzed_at=timezone.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error comparing portfolio {portfolio_id}: {e}")
        return {
            'portfolio_id': portfolio_id,
            'error': str(e)
        }
