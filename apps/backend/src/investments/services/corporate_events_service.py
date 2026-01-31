from typing import List, Dict, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, Sum
from investments.models.corporate_events import (
    EarningsEvent,
    CorporateAction,
    DividendHistory,
    EconomicEvent,
    EventAlert,
)
from investments.models import Portfolio, PortfolioPosition


class CorporateEventsService:
    def get_upcoming_earnings(self, days_ahead: int = 30) -> List[Dict]:
        start_date = timezone.now()
        end_date = start_date + timedelta(days=days_ahead)

        earnings = (
            EarningsEvent.objects.filter(
                earnings_date__gte=start_date, earnings_date__lte=end_date
            )
            .select_related("asset")
            .order_by("earnings_date")
        )

        return [
            {
                "id": e.id,
                "asset_id": e.asset.id,
                "symbol": e.asset.symbol,
                "company_name": e.asset.name,
                "date": e.earnings_date.isoformat(),
                "time": e.earnings_time,
                "quarter": f"{e.fiscal_year} {e.fiscal_quarter}",
                "estimated_eps": float(e.estimated_eps) if e.estimated_eps else None,
            }
            for e in earnings
        ]

    def get_upcoming_dividends(self, user_id: Optional[int] = None) -> List[Dict]:
        query = CorporateAction.objects.filter(
            action_type="dividend", status="announced", ex_date__gte=timezone.now()
        ).select_related("asset")

        if user_id:
            portfolio_assets = PortfolioPosition.objects.filter(
                portfolio__user_id=user_id
            ).values_list("asset_id", flat=True)
            query = query.filter(asset_id__in=list(portfolio_assets))

        actions = query.order_by("ex_date")

        return [
            {
                "id": a.id,
                "asset_id": a.asset.id,
                "symbol": a.asset.symbol,
                "ex_date": a.ex_date.isoformat() if a.ex_date else None,
                "record_date": a.record_date.isoformat() if a.record_date else None,
                "payment_date": a.payable_date.isoformat() if a.payable_date else None,
                "amount": float(a.details.get("amount", 0)),
                "frequency": a.details.get("frequency", ""),
            }
            for a in actions
        ]

    def get_corporate_actions_calendar(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        action_types: Optional[List[str]] = None,
    ) -> Dict[str, List[Dict]]:
        if not start_date:
            start_date = timezone.now()

        if not end_date:
            end_date = start_date + timedelta(days=30)

        query = CorporateAction.objects.filter(
            announcement_date__gte=start_date, announcement_date__lte=end_date
        )

        if action_types:
            query = query.filter(action_type__in=action_types)

        actions = query.select_related("asset").order_by("announcement_date")

        calendar = {}
        for action in actions:
            date_str = action.announcement_date.date().isoformat()
            if date_str not in calendar:
                calendar[date_str] = []

            calendar[date_str].append(
                {
                    "id": action.id,
                    "type": action.action_type,
                    "symbol": action.asset.symbol,
                    "description": action.description,
                    "details": action.details,
                }
            )

        return calendar

    def get_economic_calendar(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        importance: Optional[str] = None,
    ) -> List[Dict]:
        query = EconomicEvent.objects.all()

        if start_date:
            query = query.filter(event_date__gte=start_date)

        if end_date:
            query = query.filter(event_date__lte=end_date)

        if importance:
            query = query.filter(importance=importance)

        events = query.order_by("event_date")

        return [
            {
                "id": e.id,
                "name": e.name,
                "date": e.event_date.isoformat(),
                "importance": e.importance,
                "actual": float(e.actual) if e.actual else None,
                "forecast": float(e.forecast) if e.forecast else None,
                "previous": float(e.previous) if e.previous else None,
                "country": e.country,
            }
            for e in events
        ]

    def analyze_earnings_impact(self, portfolio_id: int) -> Dict:
        positions = PortfolioPosition.objects.filter(
            portfolio_id=portfolio_id
        ).select_related("asset", "portfolio")

        asset_ids = [p.asset_id for p in positions]
        upcoming_earnings = EarningsEvent.objects.filter(
            asset_id__in=asset_ids,
            earnings_date__gte=timezone.now(),
            earnings_date__lte=timezone.now() + timedelta(days=30),
        )

        total_exposure = 0
        high_impact = []
        by_sector = {}

        for earning in upcoming_earnings:
            position = next(
                (p for p in positions if p.asset_id == earning.asset_id), None
            )
            if not position:
                continue

            position_value = position.current_value or 0
            total_exposure += position_value

            impact_score = self._calculate_earnings_impact_score(earning, position)

            sector = earning.asset.sector or "Unknown"
            if sector not in by_sector:
                by_sector[sector] = 0
            by_sector[sector] += position_value

            if impact_score > 0.7:
                high_impact.append(
                    {
                        "symbol": earning.asset.symbol,
                        "date": earning.earnings_date.isoformat(),
                        "position_value": float(position_value),
                        "impact_score": impact_score,
                    }
                )

        return {
            "total_exposure": float(total_exposure),
            "high_impact_count": len(high_impact),
            "high_impact_positions": high_impact,
            "by_sector": by_sector,
        }

    def _calculate_earnings_impact_score(
        self, earning: EarningsEvent, position
    ) -> float:
        score = 0.5

        portfolio_value = (
            position.portfolio.current_value
            if hasattr(position.portfolio, "current_value")
            else 0
        )
        position_value = position.current_value or 0
        if portfolio_value > 0:
            position_weight = position_value / portfolio_value
            score += min(position_weight * 2, 0.3)

        if earning.eps_surprise:
            surprise_abs = abs(float(earning.eps_surprise))
            score += min(surprise_abs / 50, 0.2)

        return min(score, 1.0)

    def get_dividend_projection(self, asset_id: int, periods: int = 4) -> Dict:
        dividends = DividendHistory.objects.filter(asset_id=asset_id).order_by(
            "-ex_dividend_date"
        )[:12]

        if not dividends:
            return {}

        avg_dividend = sum(float(d.amount) for d in dividends) / len(dividends)

        most_recent = dividends[0]
        frequency = most_recent.frequency or "quarterly"

        frequency_map = {"monthly": 12, "quarterly": 4, "semi-annual": 2, "annual": 1}
        periods_per_year = frequency_map.get(frequency, 4)

        projected_annual = avg_dividend * periods_per_year

        return {
            "last_amount": float(dividends[0].amount),
            "last_ex_date": dividends[0].ex_dividend_date.isoformat(),
            "average_amount": float(avg_dividend),
            "frequency": frequency,
            "projected_next_12_months": float(projected_annual),
            "yield_percent": None,
        }

    def get_asset_earnings_history(self, asset_id: int, limit: int = 8) -> List[Dict]:
        earnings = EarningsEvent.objects.filter(asset_id=asset_id).order_by(
            "-earnings_date"
        )[:limit]

        return [
            {
                "quarter": f"{e.fiscal_year} {e.fiscal_quarter}",
                "date": e.earnings_date.isoformat(),
                "estimated_eps": float(e.estimated_eps) if e.estimated_eps else None,
                "actual_eps": float(e.actual_eps) if e.actual_eps else None,
                "surprise_pct": float(e.eps_surprise) if e.eps_surprise else None,
                "revenue": float(e.actual_revenue) if e.actual_revenue else None,
            }
            for e in earnings
        ]

    def get_asset_corporate_actions(self, asset_id: int, limit: int = 20) -> List[Dict]:
        actions = CorporateAction.objects.filter(asset_id=asset_id).order_by(
            "-announcement_date"
        )[:limit]

        return [
            {
                "type": a.action_type,
                "status": a.status,
                "announcement_date": a.announcement_date.isoformat(),
                "details": a.details,
                "description": a.description,
            }
            for a in actions
        ]
