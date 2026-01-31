from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import Sum, Avg, Max, Min
from django.utils import timezone
from portfolios.models.portfolio import Portfolio
from portfolios.models.holdings import Holding
from assets.models.asset import Asset
from investments.models.rebalancing import (
    TargetAllocation,
    PortfolioDrift,
    RebalancingSuggestion,
    RebalancingSession,
    TaxLot,
)
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class RebalancingService:
    """
    Portfolio rebalancing service with drift detection, trade suggestions,
    and tax-efficient rebalancing support.
    """

    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio

    def get_current_allocation(self) -> Dict[str, Dict[str, Decimal]]:
        """
        Calculate current portfolio allocation by asset class.
        Returns: {asset_class: {'value': Decimal, 'percentage': Decimal}}
        """
        holdings = self.portfolio.holdings.select_related("asset").all()

        total_value = Decimal("0")
        allocation = {}

        for holding in holdings:
            if holding.current_value and holding.current_value > 0:
                asset_class = self._get_asset_class(holding.asset)
                value = holding.current_value

                if asset_class not in allocation:
                    allocation[asset_class] = Decimal("0")
                allocation[asset_class] += value
                total_value += value

        result = {}
        for asset_class, value in allocation.items():
            result[asset_class] = {
                "value": value,
                "percentage": (value / total_value * 100)
                if total_value > 0
                else Decimal("0"),
            }

        return result

    def get_target_allocation(self) -> Dict[str, Decimal]:
        """
        Get target allocation for portfolio.
        Returns: {asset_class: target_percentage}
        """
        targets = TargetAllocation.objects.filter(portfolio=self.portfolio)
        return {t.asset_class: t.target_percentage for t in targets}

    def calculate_drift(self) -> List[PortfolioDrift]:
        """
        Calculate portfolio drift from target allocation.
        Returns list of drift records for each asset class.
        """
        current = self.get_current_allocation()
        targets = self.get_target_allocation()
        drifts = []

        all_classes = set(current.keys()) | set(targets.keys())

        for asset_class in all_classes:
            current_pct = current.get(asset_class, {}).get("percentage", Decimal("0"))
            target_pct = targets.get(asset_class, Decimal("0"))
            tolerance = self._get_tolerance(asset_class)

            drift = current_pct - target_pct
            abs_drift = abs(drift)

            if abs_drift <= tolerance:
                level = "WITHIN_TOLERANCE"
            elif abs_drift <= tolerance * 2:
                level = "WARNING"
            else:
                level = "CRITICAL"

            drift_record = PortfolioDrift.objects.create(
                portfolio=self.portfolio,
                asset_class=asset_class,
                current_percentage=current_pct,
                target_percentage=target_pct,
                drift_percentage=drift,
                drift_level=level,
            )
            drifts.append(drift_record)

        return drifts

    def get_drift_status(self) -> Dict[str, any]:
        """
        Get overall portfolio drift status.
        """
        current = self.get_current_allocation()
        targets = self.get_target_allocation()

        drifts = []
        needs_rebalancing = False

        all_classes = set(current.keys()) | set(targets.keys())

        for asset_class in all_classes:
            current_pct = current.get(asset_class, {}).get("percentage", Decimal("0"))
            target_pct = targets.get(asset_class, Decimal("0"))
            tolerance = self._get_tolerance(asset_class)

            drift = current_pct - target_pct
            abs_drift = abs(drift)

            if abs_drift > tolerance:
                needs_rebalancing = True

            drifts.append(
                {
                    "asset_class": asset_class,
                    "current_percentage": float(current_pct),
                    "target_percentage": float(target_pct),
                    "drift_percentage": float(drift),
                    "tolerance": float(tolerance),
                    "status": "OK" if abs_drift <= tolerance else "REBALANCE",
                }
            )

        return {
            "needs_rebalancing": needs_rebalancing,
            "drifts": drifts,
            "checked_at": timezone.now().isoformat(),
        }

    def generate_rebalancing_suggestions(
        self, max_trades: int = 10, prefer_tax_efficient: bool = True
    ) -> List[RebalancingSuggestion]:
        """
        Generate rebalancing trade suggestions.
        Returns list of suggested trades to reach target allocation.
        """
        current = self.get_current_allocation()
        targets = self.get_target_allocation()
        holdings = self.portfolio.holdings.select_related("asset").all()

        total_value = sum(
            h.current_value for h in holdings if h.current_value and h.current_value > 0
        )

        if total_value <= 0:
            return []

        suggestions = []
        used_trades = 0

        for asset_class, target_pct in targets.items():
            current_pct = current.get(asset_class, {}).get("percentage", Decimal("0"))
            target_value = total_value * target_pct / 100
            current_value = current.get(asset_class, {}).get("value", Decimal("0"))

            drift_value = target_value - current_value
            drift_pct = current_pct - target_pct

            tolerance = self._get_tolerance(asset_class)

            if abs(drift_pct) <= tolerance:
                continue

            action = "BUY" if drift_value > 0 else "SELL"

            holding = self._get_holding_for_class(holdings, asset_class)

            suggestion = RebalancingSuggestion(
                portfolio=self.portfolio,
                asset=holding.asset if holding else None,
                asset_class=asset_class,
                action=action,
                current_quantity=holding.quantity if holding else Decimal("0"),
                current_value=current_value,
                suggested_value=abs(drift_value),
                current_allocation=current_pct,
                target_allocation=target_pct,
                priority=self._calculate_priority(abs(drift_pct)),
                tax_implication=self._estimate_tax_implication(holding)
                if action == "SELL"
                else "NEUTRAL",
                estimated_trade_value=abs(drift_value),
                reason=f"{action} {asset_class} to reach target allocation of {target_pct}%",
            )
            suggestions.append(suggestion)
            used_trades += 1

            if used_trades >= max_trades:
                break

        return suggestions[:max_trades]

    def set_target_allocation(
        self, allocations: Dict[str, Dict[str, Decimal]], replace_existing: bool = True
    ) -> List[TargetAllocation]:
        """
        Set target allocation for portfolio.
        allocations: {asset_class: {'target': Decimal, 'tolerance': Decimal}}
        """
        if replace_existing:
            TargetAllocation.objects.filter(portfolio=self.portfolio).delete()

        targets = []
        for asset_class, config in allocations.items():
            target = TargetAllocation.objects.create(
                portfolio=self.portfolio,
                asset_class=asset_class,
                target_percentage=config["target"],
                tolerance_percentage=config.get(
                    "tolerance", self._get_tolerance(asset_class)
                ),
            )
            targets.append(target)

        return targets

    def calculate_tax_lots(self) -> List[TaxLot]:
        """
        Calculate and update tax lot information for portfolio.
        Used for tax-efficient rebalancing decisions.
        """
        holdings = self.portfolio.holdings.select_related("asset").all()
        tax_lots = []
        today = timezone.now().date()

        for holding in holdings:
            if not holding.asset or not holding.purchase_date:
                continue

            cost_basis = (
                holding.purchase_price * holding.quantity
                if holding.purchase_price
                else Decimal("0")
            )
            current_value = holding.current_value or Decimal("0")
            unrealized_pnl = holding.unrealized_pnl or Decimal("0")

            gain_loss_pct = (
                (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else Decimal("0")
            )

            holding_period = (today - holding.purchase_date).days
            is_long_term = holding_period >= 365

            tax_lot = TaxLot.objects.update_or_create(
                portfolio=self.portfolio,
                asset=holding.asset,
                purchase_date=holding.purchase_date,
                defaults={
                    "quantity": holding.quantity,
                    "cost_basis": cost_basis,
                    "current_value": current_value,
                    "purchase_date": holding.purchase_date,
                    "current_price": holding.current_price or Decimal("0"),
                    "unrealized_gain_loss": unrealized_pnl,
                    "gain_loss_percentage": gain_loss_pct,
                    "holding_period_days": holding_period,
                    "is_long_term": is_long_term,
                },
            )
            tax_lots.append(tax_lot[0])

        return tax_lots

    def get_tax_loss_harvesting_opportunities(self) -> List[Dict]:
        """
        Get tax-loss harvesting opportunities.
        Returns positions with unrealized losses sorted by magnitude.
        """
        tax_lots = TaxLot.objects.filter(
            portfolio=self.portfolio, unrealized_gain_loss__lt=Decimal("0")
        ).order_by("unrealized_gain_loss")

        opportunities = []
        for lot in tax_lots:
            opportunities.append(
                {
                    "asset": lot.asset.symbol if lot.asset else None,
                    "quantity": lot.quantity,
                    "cost_basis": lot.cost_basis,
                    "current_value": lot.current_value,
                    "unrealized_loss": abs(lot.unrealized_gain_loss),
                    "loss_percentage": abs(lot.gain_loss_percentage),
                    "purchase_date": lot.purchase_date,
                    "is_long_term": lot.is_long_term,
                    "wash_sale_risk": lot.wash_sale_risk,
                }
            )

        return opportunities

    def create_rebalancing_session(
        self, name: str, max_trades: int = 10, tax_efficient: bool = True
    ) -> RebalancingSession:
        """
        Create a rebalancing session with suggestions.
        """
        suggestions = self.generate_rebalancing_suggestions(
            max_trades=max_trades, prefer_tax_efficient=tax_efficient
        )

        total_value = sum(
            s.estimated_trade_value for s in suggestions if s.action == "BUY"
        )

        session = RebalancingSession.objects.create(
            portfolio=self.portfolio,
            name=name,
            status="PENDING_REVIEW",
            total_trades=len(suggestions),
            estimated_total_value=total_value,
        )

        for suggestion in suggestions:
            suggestion.session = session
            suggestion.save()

        return session

    def execute_rebalancing_session(self, session_id: str) -> Dict:
        """
        Execute a rebalancing session.
        This is a simulation - actual execution requires broker integration.
        """
        session = RebalancingSession.objects.get(
            id=session_id, portfolio=self.portfolio
        )

        suggestions = RebalancingSuggestion.objects.filter(
            session=session, status="PENDING"
        )

        total_executed = Decimal("0")
        tax_impact = Decimal("0")

        for suggestion in suggestions:
            suggestion.status = "EXECUTED"
            suggestion.executed_at = timezone.now()
            suggestion.save()
            total_executed += suggestion.estimated_trade_value

            if suggestion.tax_implication == "LOSS":
                tax_impact += suggestion.estimated_trade_value * Decimal("0.3")

        session.status = "COMPLETED"
        session.executed_at = timezone.now()
        session.actual_total_value = total_executed
        session.tax_impact = tax_impact
        session.save()

        return {
            "session_id": str(session.id),
            "trades_executed": suggestions.count(),
            "total_value": float(total_executed),
            "tax_impact": float(tax_impact),
            "completed_at": session.executed_at.isoformat(),
        }

    def what_if_analysis(self, proposed_changes: Dict[str, Decimal]) -> Dict:
        """
        What-if analysis for proposed rebalancing changes.
        proposed_changes: {asset_class: new_percentage}
        """
        current = self.get_current_allocation()
        total_allocation = sum(proposed_changes.values())

        if total_allocation > Decimal("100.05") or total_allocation < Decimal("99.95"):
            return {
                "valid": False,
                "error": "Proposed allocation must sum to 100%",
                "current_sum": float(total_allocation),
            }

        holdings = self.portfolio.holdings.select_related("asset").all()
        total_value = sum(
            h.current_value for h in holdings if h.current_value and h.current_value > 0
        )

        trades = []
        for asset_class, new_pct in proposed_changes.items():
            current_pct = current.get(asset_class, {}).get("percentage", Decimal("0"))
            drift = new_pct - current_pct

            if abs(drift) < Decimal("0.5"):
                continue

            holding = self._get_holding_for_class(holdings, asset_class)
            trade_value = total_value * drift / 100

            trades.append(
                {
                    "asset_class": asset_class,
                    "action": "BUY" if drift > 0 else "SELL",
                    "current_allocation": float(current_pct),
                    "proposed_allocation": float(new_pct),
                    "trade_value": float(abs(trade_value)),
                    "drift": float(drift),
                    "shares_affected": holding.quantity if holding else None,
                }
            )

        return {
            "valid": True,
            "trades": trades,
            "total_trades_needed": len(trades),
            "estimated_turnover": sum(abs(t["trade_value"]) for t in trades)
            / total_value
            * 100
            if total_value > 0
            else 0,
        }

    def _get_asset_class(self, asset: Asset) -> str:
        """Get asset class from asset."""
        if not asset:
            return "other"

        asset_type = str(asset.asset_type).lower() if asset.asset_type else ""

        if asset_type in ["stock", "equity"]:
            return "stock"
        elif asset_type in ["bond", "fixed_income"]:
            return "bond"
        elif asset_type in ["crypto", "cryptocurrency"]:
            return "crypto"
        elif asset_type in ["etf", "fund"]:
            return "etf"
        elif asset_type in ["real_estate", "reit"]:
            return "real_estate"
        elif asset_type in ["cash", "money_market"]:
            return "cash"
        elif asset_type in ["commodity", "gold", "silver"]:
            return "commodity"
        else:
            return "other"

    def _get_tolerance(self, asset_class: str) -> Decimal:
        """Get tolerance for asset class."""
        try:
            target = TargetAllocation.objects.get(
                portfolio=self.portfolio, asset_class=asset_class
            )
            return target.tolerance_percentage
        except TargetAllocation.DoesNotExist:
            return Decimal("5.00")

    def _get_holding_for_class(self, holdings, asset_class: str) -> Optional[Holding]:
        """Get holding for asset class."""
        for holding in holdings:
            if self._get_asset_class(holding.asset) == asset_class:
                return holding
        return None

    def _calculate_priority(self, drift_percentage: Decimal) -> str:
        """Calculate priority based on drift magnitude."""
        if drift_percentage > Decimal("15"):
            return "HIGH"
        elif drift_percentage > Decimal("8"):
            return "MEDIUM"
        else:
            return "LOW"

    def _estimate_tax_implication(self, holding: Optional[Holding]) -> str:
        """Estimate tax implication for selling holding."""
        if not holding:
            return "NEUTRAL"

        if holding.unrealized_pnl and holding.unrealized_pnl < 0:
            return "LOSS"
        elif holding.unrealized_pnl and holding.unrealized_pnl > 0:
            return "GAIN"
        else:
            return "NEUTRAL"
