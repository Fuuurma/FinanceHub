from django.db import transaction
from django.shortcuts import get_object_or_404
from assets.models.asset import Asset
from portfolios.models.holdings import Holding
from decimal import Decimal

from portfolios.models.portfolio import Portfolio


class HoldingService:
    @staticmethod
    @transaction.atomic
    def add_holding(portfolio: Portfolio, asset_id: str, quantity: Decimal):
        asset = get_object_or_404(Asset, id=asset_id)
        holding, created = Holding.objects.get_or_create(
            portfolio=portfolio, asset=asset, defaults={"quantity": quantity}
        )
        if not created:
            holding.quantity += quantity
            holding.save()
        return holding
