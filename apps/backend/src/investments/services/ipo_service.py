from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone


class IPOCalendarService:
    def __init__(self):
        pass

    def get_upcoming_ipos(
        self,
        days_ahead: int = 90,
        status: Optional[str] = None,
        sector: Optional[str] = None,
        exchange: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        try:
            from investments.models.ipo import IPOCalendar

            qs = IPOCalendar.objects.all()

            if status:
                qs = qs.filter(status=status)
            else:
                qs = qs.filter(status__in=["upcoming", "filed", "updated"])

            if sector:
                qs = qs.filter(sector=sector)

            if exchange:
                qs = qs.filter(exchange=exchange)

            if days_ahead > 0:
                end_date = timezone.now().date() + timedelta(days=days_ahead)
                qs = qs.filter(
                    expected_date__gte=timezone.now().date(),
                    expected_date__lte=end_date,
                )

            total_count = qs.count()

            results = list(qs.order_by("expected_date")[offset : offset + limit])

            ipo_data = [self._format_ipo(ipo) for ipo in results]

            return {
                "ipos": ipo_data,
                "total_count": total_count,
                "filters_applied": {
                    "days_ahead": days_ahead,
                    "status": status,
                    "sector": sector,
                    "exchange": exchange,
                },
            }
        except Exception as e:
            return {"ipos": [], "total_count": 0, "error": str(e)}

    def get_recent_ipos(
        self, days_back: int = 90, limit: int = 50, offset: int = 0
    ) -> Dict[str, Any]:
        try:
            from investments.models.ipo import IPOCalendar

            qs = IPOCalendar.objects.filter(status="listed")

            start_date = timezone.now().date() - timedelta(days=days_back)
            qs = qs.filter(listed_date__gte=start_date)

            total_count = qs.count()

            results = list(qs.order_by("-listed_date")[offset : offset + limit])

            ipo_data = [self._format_ipo(ipo) for ipo in results]

            return {
                "ipos": ipo_data,
                "total_count": total_count,
                "period_days": days_back,
            }
        except Exception as e:
            return {"ipos": [], "total_count": 0, "error": str(e)}

    def get_ipo_detail(self, ipo_id: int) -> Dict:
        try:
            from investments.models.ipo import IPOCalendar

            ipo = IPOCalendar.objects.get(id=ipo_id)
            return self._format_ipo(ipo)
        except IPOCalendar.DoesNotExist:
            return {"error": "IPO not found"}
        except Exception as e:
            return {"error": str(e)}

    def _format_ipo(self, ipo) -> Dict:
        return {
            "id": ipo.id,
            "company_name": ipo.company_name,
            "ticker": ipo.ticker,
            "exchange": ipo.exchange,
            "expected_price_min": float(ipo.expected_price_min)
            if ipo.expected_price_min
            else None,
            "expected_price_max": float(ipo.expected_price_max)
            if ipo.expected_price_max
            else None,
            "actual_price": float(ipo.actual_price) if ipo.actual_price else None,
            "shares_offered": ipo.shares_offered,
            "deal_size": float(ipo.deal_size) if ipo.deal_size else None,
            "filed_date": ipo.filed_date.isoformat() if ipo.filed_date else None,
            "expected_date": ipo.expected_date.isoformat()
            if ipo.expected_date
            else None,
            "priced_date": ipo.priced_date.isoformat() if ipo.priced_date else None,
            "listed_date": ipo.listed_date.isoformat() if ipo.listed_date else None,
            "status": ipo.status,
            "sector": ipo.sector,
            "industry": ipo.industry,
            "description": ipo.description[:500] + "..."
            if ipo.description and len(ipo.description) > 500
            else ipo.description or "",
            "lead_underwriter": ipo.lead_underwriter,
            "underwriters": ipo.underwriters,
            "expected_valuation": float(ipo.expected_valuation)
            if ipo.expected_valuation
            else None,
            "raised_amount": float(ipo.raised_amount) if ipo.raised_amount else None,
            "market_cap_estimate": float(ipo.market_cap_estimate)
            if ipo.market_cap_estimate
            else None,
            "ipo_day_change": float(ipo.ipo_day_change) if ipo.ipo_day_change else None,
            "ipo_day_change_pct": float(ipo.ipo_day_change_pct)
            if ipo.ipo_day_change_pct
            else None,
        }

    def get_sectors(self) -> List[Dict]:
        try:
            from investments.models.ipo import IPOCalendar

            sectors = (
                IPOCalendar.objects.exclude(sector="")
                .values_list("sector", flat=True)
                .distinct()
            )
            return [{"sector": s} for s in sorted(set(sectors)) if s]
        except Exception:
            return []

    def get_exchanges(self) -> List[Dict]:
        try:
            from investments.models.ipo import IPOCalendar

            exchanges = (
                IPOCalendar.objects.exclude(exchange="")
                .values_list("exchange", flat=True)
                .distinct()
            )
            return [{"exchange": e} for e in sorted(set(exchanges)) if e]
        except Exception:
            return []

    def get_stats(self) -> Dict:
        try:
            from investments.models.ipo import IPOCalendar

            now = timezone.now().date()

            upcoming = IPOCalendar.objects.filter(
                status__in=["upcoming", "filed", "updated"], expected_date__gte=now
            ).count()
            this_week = IPOCalendar.objects.filter(
                status__in=["upcoming", "filed", "updated"],
                expected_date__gte=now,
                expected_date__lte=now + timedelta(days=7),
            ).count()
            this_month = IPOCalendar.objects.filter(
                status__in=["upcoming", "filed", "updated"],
                expected_date__gte=now,
                expected_date__lte=now + timedelta(days=30),
            ).count()
            last_30_days = IPOCalendar.objects.filter(
                status="listed", listed_date__gte=now - timedelta(days=30)
            ).count()

            return {
                "upcoming_count": upcoming,
                "this_week_count": this_week,
                "this_month_count": this_month,
                "last_30_days_listed": last_30_days,
            }
        except Exception:
            return {
                "upcoming_count": 0,
                "this_week_count": 0,
                "this_month_count": 0,
                "last_30_days_listed": 0,
            }

    def add_to_watchlist(self, user_id: int, ipo_id: int, notes: str = "") -> Dict:
        try:
            from investments.models.ipo import IPOWatchlist

            watchlist, created = IPOWatchlist.objects.get_or_create(
                user_id=user_id, ipo_id=ipo_id, defaults={"notes": notes}
            )

            return {
                "success": True,
                "added": created,
                "message": "Added to watchlist" if created else "Already in watchlist",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def remove_from_watchlist(self, user_id: int, ipo_id: int) -> Dict:
        try:
            from investments.models.ipo import IPOWatchlist

            deleted, _ = IPOWatchlist.objects.filter(
                user_id=user_id, ipo_id=ipo_id
            ).delete()

            return {
                "success": True,
                "removed": deleted > 0,
                "message": "Removed from watchlist"
                if deleted > 0
                else "Not in watchlist",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_watchlist(self, user_id: int) -> List[Dict]:
        try:
            from investments.models.ipo import IPOCalendar, IPOWatchlist

            watchlist_items = IPOWatchlist.objects.filter(user_id=user_id).order_by(
                "-added_at"
            )
            ipo_ids = [item.ipo_id for item in watchlist_items]

            if not ipo_ids:
                return []

            ipos = IPOCalendar.objects.filter(id__in=ipo_ids)

            ipo_map = {ipo.id: self._format_ipo(ipo) for ipo in ipos}

            watchlist = []
            for item in watchlist_items:
                if item.ipo_id in ipo_map:
                    watchlist.append(
                        {
                            **ipo_map[item.ipo_id],
                            "added_at": item.added_at.isoformat(),
                            "notes": item.notes,
                        }
                    )

            return watchlist
        except Exception:
            return []

    def create_alert(
        self,
        user_id: int,
        alert_type: str = "upcoming",
        sector: str = "",
        exchange: str = "",
        min_deal_size: float = None,
        max_deal_size: float = None,
    ) -> Dict:
        try:
            from investments.models.ipo import IPOAlert

            alert = IPOAlert.objects.create(
                user_id=user_id,
                alert_type=alert_type,
                sector=sector,
                exchange=exchange,
                min_deal_size=Decimal(str(min_deal_size)) if min_deal_size else None,
                max_deal_size=Decimal(str(max_deal_size)) if max_deal_size else None,
            )

            return {"success": True, "id": alert.id, "alert_type": alert_type}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_alerts(self, user_id: int) -> List[Dict]:
        try:
            from investments.models.ipo import IPOAlert

            alerts = IPOAlert.objects.filter(user_id=user_id, is_active=True)
            return [
                {
                    "id": a.id,
                    "alert_type": a.alert_type,
                    "sector": a.sector,
                    "exchange": a.exchange,
                    "min_deal_size": float(a.min_deal_size)
                    if a.min_deal_size
                    else None,
                    "max_deal_size": float(a.max_deal_size)
                    if a.max_deal_size
                    else None,
                    "is_active": a.is_active,
                    "created_at": a.created_at.isoformat(),
                }
                for a in alerts
            ]
        except Exception:
            return []

    def delete_alert(self, user_id: int, alert_id: int) -> Dict:
        try:
            from investments.models.ipo import IPOAlert

            deleted = IPOAlert.objects.filter(id=alert_id, user_id=user_id).delete()
            return {"success": True, "deleted": deleted[0] > 0}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_spacs(
        self, status: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> Dict:
        try:
            from investments.models.ipo import SPACTracker

            qs = SPACTracker.objects.all()

            if status:
                qs = qs.filter(status=status)

            total_count = qs.count()

            results = list(qs.order_by("-trust_size")[offset : offset + limit])

            spac_data = [
                {
                    "id": spac.id,
                    "ticker": spac.ticker,
                    "company_name": spac.company_name,
                    "trust_size": float(spac.trust_size) if spac.trust_size else None,
                    "redemption_rate": float(spac.redemption_rate)
                    if spac.redemption_rate
                    else None,
                    "target_sector": spac.target_sector,
                    "target_industry": spac.target_industry,
                    "expected_completion_date": spac.expected_completion_date.isoformat()
                    if spac.expected_completion_date
                    else None,
                    "status": spac.status,
                    "current_price": float(spac.current_price)
                    if spac.current_price
                    else None,
                    "nav_premium": float(spac.nav_premium)
                    if spac.nav_premium
                    else None,
                    "partner": spac.partner,
                    "sponsor": spac.sponsor,
                }
                for spac in results
            ]

            return {"spacs": spac_data, "total_count": total_count}
        except Exception as e:
            return {"spacs": [], "total_count": 0, "error": str(e)}

    def get_calendar_summary(self, months: int = 3) -> Dict:
        try:
            from investments.models.ipo import IPOCalendar

            now = timezone.now().date()
            end_date = now + timedelta(days=months * 30)

            qs = IPOCalendar.objects.filter(
                status__in=["upcoming", "filed", "updated"],
                expected_date__gte=now,
                expected_date__lte=end_date,
            )

            monthly_data = {}
            for ipo in qs:
                if ipo.expected_date:
                    month_key = ipo.expected_date.strftime("%Y-%m")
                    if month_key not in monthly_data:
                        monthly_data[month_key] = {
                            "count": 0,
                            "total_deal_size": 0,
                            "ipos": [],
                        }
                    monthly_data[month_key]["count"] += 1
                    if ipo.deal_size:
                        monthly_data[month_key]["total_deal_size"] += float(
                            ipo.deal_size
                        )
                    monthly_data[month_key]["ipos"].append(
                        {
                            "id": ipo.id,
                            "company_name": ipo.company_name,
                            "ticker": ipo.ticker,
                            "expected_date": ipo.expected_date.isoformat(),
                            "deal_size": float(ipo.deal_size)
                            if ipo.deal_size
                            else None,
                        }
                    )

            return {
                "summary": monthly_data,
                "total_upcoming": qs.count(),
                "period_months": months,
            }
        except Exception as e:
            return {"summary": {}, "total_upcoming": 0, "error": str(e)}
