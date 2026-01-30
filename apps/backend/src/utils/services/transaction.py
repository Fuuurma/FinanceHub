from decimal import Decimal
from assets.models.asset import Asset
from investments.models.transaction import Transaction
from portfolios.models.portfolio import Portfolio
from utils.services.holding import HoldingService
from django.shortcuts import get_object_or_404
from django.db import transaction


class TransactionService:

    @staticmethod
    @transaction.atomic
    def record_transaction(portfolio: Portfolio, data: dict):
        asset = get_object_or_404(Asset, id=data.pop("asset_id"))
        total_amount = data["price_per_share"] * (
            data.get("quantity") or Decimal("1")
        ) + data.get("fees", 0)

        transaction = Transaction.objects.create(
            portfolio=portfolio, asset=asset, total_amount=total_amount, **data
        )

        # Update holding quantity
        if data["transaction_type"] in ["buy", "sell"]:
            holding = HoldingService.add_holding(
                portfolio,
                asset.id,
                (
                    data["quantity"]
                    if data["transaction_type"] == "buy"
                    else -data["quantity"]
                ),
            )
            if holding.quantity <= 0:
                holding.soft_delete()

        return transaction
