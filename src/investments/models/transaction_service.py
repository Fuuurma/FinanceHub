# apps/investments/services.py
from django.db import transaction

from investments.models.transaction import Transaction
from portfolios.models.holdings import Holding


class TransactionService:
    @staticmethod
    @transaction.atomic
    def record_buy(user, portfolio_id, asset_id, quantity, price, fees=0):
        # 1. Create the immutable ledger entry
        tx = Transaction.objects.create(
            portfolio_id=portfolio_id,
            asset_id=asset_id,
            tx_type_id="BUY_UUID",  # Reference to your BUY type
            quantity=quantity,
            price_per_unit=price,
            fees=fees,
            total_amount=(quantity * price) + fees,
        )

        # 2. Update or Create the Holding
        holding, created = Holding.objects.get_or_create(
            portfolio_id=portfolio_id, asset_id=asset_id
        )

        # Calculate new average cost
        new_total_qty = holding.total_quantity + quantity
        # (Professional Weighted Average Cost logic here)
        holding.total_quantity = new_total_qty
        holding.save()

        return tx
