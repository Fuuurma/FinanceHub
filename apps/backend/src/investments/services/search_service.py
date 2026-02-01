from typing import List, Dict, Optional, Any
from django.db.models import Q, Case, When, IntegerField
from django.utils import timezone
import re


class UniversalSearchService:
    WEIGHTS = {
        "symbol_exact_match": 100,
        "symbol_starts_with": 80,
        "name_starts_with": 60,
        "name_contains": 40,
        "sector_match": 20,
        "popular_asset": 10,
    }

    ASSET_TYPES = [
        ("stock", "Stocks"),
        ("etf", "ETFs"),
        ("crypto", "Cryptocurrency"),
        ("forex", "Forex"),
        ("commodity", "Commodities"),
        ("bond", "Bonds"),
        ("mutual_fund", "Mutual Funds"),
    ]

    SCREEN_CATEGORIES = [
        ("value", "Value Investing"),
        ("growth", "Growth Investing"),
        ("dividend", "Dividend Stocks"),
        ("momentum", "Momentum Trading"),
        ("quality", "Quality Companies"),
        ("small_cap", "Small Cap Opportunities"),
        ("etf", "ETF Screener"),
        ("crypto", "Crypto Screener"),
    ]

    def __init__(self):
        pass

    def universal_search(
        self,
        query: str,
        asset_types: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0,
        user_id: int = 0,
    ) -> Dict[str, Any]:
        if not query or len(query.strip()) < 1:
            return {"results": [], "total_count": 0, "suggestions": []}

        query = query.strip()

        try:
            from investments.models import Asset

            assets_qs = Asset.objects.all()

            if asset_types:
                assets_qs = assets_qs.filter(asset_type__in=asset_types)

            assets_qs = self._annotate_relevance(assets_qs, query)

            total_count = assets_qs.count()

            results = list(assets_qs.order_by("-relevance")[offset : offset + limit])

            formatted_results = [self._format_search_result(asset) for asset in results]

            suggestions = []
            if len(formatted_results) < 5:
                suggestions = self._generate_suggestions(query, asset_types)

            return {
                "results": formatted_results,
                "total_count": total_count,
                "suggestions": suggestions,
            }
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            return {"results": [], "total_count": 0, "suggestions": [], "error": str(e)}

    def _annotate_relevance(self, queryset, query: str):
        query_lower = query.lower()

        exact_symbol = Case(
            When(
                Q(symbol__iexact=query_lower), then=self.WEIGHTS["symbol_exact_match"]
            ),
            default=0,
            output_field=IntegerField(),
        )

        symbol_starts = Case(
            When(
                Q(symbol__istartswith=query_lower),
                then=self.WEIGHTS["symbol_starts_with"],
            ),
            default=0,
            output_field=IntegerField(),
        )

        name_starts = Case(
            When(
                Q(name__istartswith=query_lower), then=self.WEIGHTS["name_starts_with"]
            ),
            default=0,
            output_field=IntegerField(),
        )

        name_contains = Case(
            When(Q(name__icontains=query_lower), then=self.WEIGHTS["name_contains"]),
            default=0,
            output_field=IntegerField(),
        )

        return queryset.annotate(
            relevance=exact_symbol + symbol_starts + name_starts + name_contains
        )

    def _format_search_result(self, asset) -> Dict:
        try:
            current_price = float(getattr(asset, "current_price", 0) or 0)
            change_pct = float(getattr(asset, "change_pct", 0) or 0)

            return {
                "id": asset.id,
                "symbol": asset.symbol,
                "name": asset.name,
                "asset_type": asset.asset_type,
                "exchange": getattr(asset, "exchange", "") or "",
                "current_price": current_price,
                "change_pct": change_pct,
                "market_cap": getattr(asset, "market_cap", None),
                "volume": getattr(asset, "volume", None),
                "sector": getattr(asset, "sector", "") or "",
                "relevance_score": getattr(asset, "relevance", 0),
            }
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError):
            return {
                "id": getattr(asset, "id", 0),
                "symbol": getattr(asset, "symbol", "UNKNOWN"),
                "name": getattr(asset, "name", "Unknown"),
                "asset_type": getattr(asset, "asset_type", "stock"),
            }

    def _generate_suggestions(
        self, query: str, asset_types: Optional[List[str]] = None
    ) -> List[Dict]:
        suggestions = []

        try:
            from investments.models import Asset

            assets_qs = Asset.objects.filter(
                Q(symbol__istartswith=query.upper()[:4]) | Q(name__icontains=query)
            )

            if asset_types:
                assets_qs = assets_qs.filter(asset_type__in=asset_types)

            for asset in assets_qs[:5]:
                suggestions.append(
                    {
                        "symbol": asset.symbol,
                        "name": asset.name,
                        "asset_type": asset.asset_type,
                    }
                )
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError):
            pass

        return suggestions

    def advanced_search(
        self,
        query: str = "",
        filters: Optional[Dict] = None,
        sort_by: str = "market_cap",
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0,
        user_id: int = 0,
    ) -> Dict[str, Any]:
        try:
            from investments.models import Asset

            assets_qs = Asset.objects.all()

            if query:
                assets_qs = self._annotate_relevance(assets_qs, query)
                assets_qs = assets_qs.filter(relevance__gt=0)
            else:
                assets_qs = assets_qs.annotate(relevance=self.WEIGHTS["popular_asset"])

            if filters:
                assets_qs = self._apply_filters(assets_qs, filters)

            total_count = assets_qs.count()

            order_prefix = "-" if sort_order == "desc" else ""
            valid_sort_fields = [
                "market_cap",
                "volume",
                "current_price",
                "change_pct",
                "dividend_yield",
                "pe_ratio",
                "relevance",
            ]
            sort_field = sort_by if sort_by in valid_sort_fields else "market_cap"

            results = list(
                assets_qs.order_by(f"{order_prefix}{sort_field}")[
                    offset : offset + limit
                ]
            )

            formatted_results = [self._format_search_result(asset) for asset in results]

            return {
                "results": formatted_results,
                "total_count": total_count,
                "filters_applied": filters or {},
                "sort": {"field": sort_field, "order": sort_order},
            }
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            return {"results": [], "total_count": 0, "error": str(e)}

    def _apply_filters(self, queryset, filters: Dict):
        if "asset_type" in filters and filters["asset_type"]:
            queryset = queryset.filter(asset_type__in=filters["asset_type"])

        if "sector" in filters and filters["sector"]:
            queryset = queryset.filter(sector__in=filters["sector"])

        if "exchange" in filters and filters["exchange"]:
            queryset = queryset.filter(exchange__in=filters["exchange"])

        if "market_cap_min" in filters:
            queryset = queryset.filter(market_cap__gte=filters["market_cap_min"])

        if "market_cap_max" in filters:
            queryset = queryset.filter(market_cap__lte=filters["market_cap_max"])

        if "pe_ratio_min" in filters:
            queryset = queryset.filter(pe_ratio__gte=filters["pe_ratio_min"])

        if "pe_ratio_max" in filters:
            queryset = queryset.filter(pe_ratio__lte=filters["pe_ratio_max"])

        if "dividend_yield_min" in filters:
            queryset = queryset.filter(
                dividend_yield__gte=filters["dividend_yield_min"]
            )

        if "volume_min" in filters:
            queryset = queryset.filter(volume__gte=filters["volume_min"])

        if "price_min" in filters:
            queryset = queryset.filter(current_price__gte=filters["price_min"])

        if "price_max" in filters:
            queryset = queryset.filter(current_price__lte=filters["price_max"])

        if "change_pct_min" in filters:
            queryset = queryset.filter(change_pct__gte=filters["change_pct_min"])

        if "change_pct_max" in filters:
            queryset = queryset.filter(change_pct__lte=filters["change_pct_max"])

        if "rsi_min" in filters or "rsi_max" in filters:
            from investments.models import TechnicalIndicator

            rsi_assets = TechnicalIndicator.objects.filter(indicator="rsi")
            if "rsi_min" in filters:
                rsi_assets = rsi_assets.filter(value__gte=filters["rsi_min"])
            if "rsi_max" in filters:
                rsi_assets = rsi_assets.filter(value__lte=filters["rsi_max"])
            asset_ids = list(rsi_assets.values_list("asset_id", flat=True))
            queryset = queryset.filter(id__in=asset_ids)

        return queryset

    def get_sectors(self) -> List[Dict]:
        try:
            from investments.models import Asset

            sectors = (
                Asset.objects.exclude(sector__isnull=True)
                .exclude(sector="")
                .values_list("sector", flat=True)
                .distinct()
            )
            return [{"sector": s} for s in sorted(set(sectors)) if s]
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError):
            return []

    def get_exchanges(self) -> List[Dict]:
        try:
            from investments.models import Asset

            exchanges = (
                Asset.objects.exclude(exchange__isnull=True)
                .exclude(exchange="")
                .values_list("exchange", flat=True)
                .distinct()
            )
            return [{"exchange": e} for e in sorted(set(exchanges)) if e]
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError):
            return []

    def get_screen_templates(self, category: Optional[str] = None) -> List[Dict]:
        try:
            from investments.models.search import ScreenTemplate

            templates = ScreenTemplate.objects.all()
            if category:
                templates = templates.filter(category=category)

            return [
                {
                    "id": t.id,
                    "name": t.name,
                    "category": t.category,
                    "description": t.description,
                    "filters": t.filters,
                    "is_featured": t.is_featured,
                }
                for t in templates.order_by("-is_featured", "-use_count")[:20]
            ]
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError):
            return []

    def get_filter_options(self) -> Dict:
        return {
            "asset_types": [{"value": v, "label": l} for v, l in self.ASSET_TYPES],
            "sectors": self.get_sectors(),
            "exchanges": self.get_exchanges(),
            "sort_options": [
                {"value": "market_cap", "label": "Market Cap"},
                {"value": "volume", "label": "Volume"},
                {"value": "current_price", "label": "Price"},
                {"value": "change_pct", "label": "Change %"},
                {"value": "dividend_yield", "label": "Dividend Yield"},
                {"value": "pe_ratio", "label": "P/E Ratio"},
            ],
        }

    def save_search(
        self,
        user_id: int,
        name: str,
        query: str = "",
        filters: Optional[Dict] = None,
        sort_by: str = "market_cap",
        sort_order: str = "desc",
        description: str = "",
    ) -> Dict:
        try:
            from investments.models.search import SavedSearch

            search = SavedSearch.objects.create(
                user_id=user_id,
                name=name,
                search_query=query,
                filters=filters or {},
                sort_by=sort_by,
                sort_order=sort_order,
                description=description,
            )

            return {"success": True, "id": search.id, "name": search.name}
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            return {"success": False, "error": str(e)}

    def get_saved_searches(self, user_id: int) -> List[Dict]:
        try:
            from investments.models.search import SavedSearch

            searches = SavedSearch.objects.filter(user_id=user_id)
            return [
                {
                    "id": s.id,
                    "name": s.name,
                    "query": s.search_query,
                    "filters": s.filters,
                    "sort_by": s.sort_by,
                    "sort_order": s.sort_order,
                    "is_default": s.is_default,
                    "use_count": s.use_count,
                    "last_used_at": s.last_used_at.isoformat()
                    if s.last_used_at
                    else None,
                }
                for s in searches.order_by("-is_default", "-use_count")
            ]
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError):
            return []

    def create_comparison(
        self,
        user_id: int,
        name: str,
        asset_ids: List[int],
        metrics: Optional[List[str]] = None,
    ) -> Dict:
        try:
            from investments.models.search import AssetComparison

            comparison = AssetComparison.objects.create(
                user_id=user_id, name=name, assets=asset_ids, metrics=metrics or []
            )

            return {"success": True, "id": comparison.id, "name": comparison.name}
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            return {"success": False, "error": str(e)}

    def get_comparison(self, comparison_id: int) -> Dict:
        try:
            from investments.models.search import AssetComparison
            from investments.models import Asset

            comparison = AssetComparison.objects.get(id=comparison_id)
            asset_ids = comparison.assets or []

            assets = Asset.objects.filter(id__in=asset_ids) if asset_ids else []

            asset_data = []
            for asset in assets:
                asset_data.append(
                    {
                        "id": asset.id,
                        "symbol": asset.symbol,
                        "name": asset.name,
                        "asset_type": asset.asset_type,
                        "current_price": float(getattr(asset, "current_price", 0) or 0),
                        "market_cap": getattr(asset, "market_cap", None),
                        "pe_ratio": getattr(asset, "pe_ratio", None),
                        "dividend_yield": getattr(asset, "dividend_yield", None),
                        "volume": getattr(asset, "volume", None),
                        "sector": getattr(asset, "sector", "") or "",
                    }
                )

            return {
                "id": comparison.id,
                "name": comparison.name,
                "assets": asset_data,
                "metrics": comparison.metrics,
            }
        except AssetComparison.DoesNotExist:
            return {"error": "Comparison not found"}
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            return {"error": str(e)}
