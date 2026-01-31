from django.conf import settings
from cryptography.fernet import Fernet
from typing import Dict, Type, Optional, Any
from decimal import Decimal
from datetime import datetime
import logging

from .models import (
    BrokerConnection,
    BrokerPosition,
    BrokerTransaction,
    BrokerOrder,
    PortfolioSyncLog,
)
from .integrations import BaseBroker, AlpacaBroker, BinanceBroker, CoinbaseBroker

logger = logging.getLogger(__name__)

BROKER_CLASSES: Dict[str, Type[BaseBroker]] = {
    "alpaca": AlpacaBroker,
    "binance": BinanceBroker,
    "coinbase": CoinbaseBroker,
}


class EncryptionService:
    @staticmethod
    def encrypt(data: bytes) -> bytes:
        fernet = Fernet(settings.ENCRYPTION_KEY.encode())
        return fernet.encrypt(data)

    @staticmethod
    def decrypt(data: bytes) -> bytes:
        fernet = Fernet(settings.ENCRYPTION_KEY.encode())
        return fernet.decrypt(data)


class BrokerService:
    @staticmethod
    def get_broker_class(broker_name: str) -> Optional[Type[BaseBroker]]:
        return BROKER_CLASSES.get(broker_name)

    @staticmethod
    def create_broker_from_connection(connection: BrokerConnection) -> BaseBroker:
        broker_class = BrokerService.get_broker_class(connection.broker)
        if not broker_class:
            raise ValueError(f"Unknown broker: {connection.broker}")

        api_key = EncryptionService.decrypt(connection.api_key_encrypted)
        api_secret = EncryptionService.decrypt(connection.api_secret_encrypted)
        passphrase = None
        if connection.passphrase_encrypted:
            passphrase = EncryptionService.decrypt(connection.passphrase_encrypted)

        return broker_class(
            api_key=api_key,
            api_secret=api_secret,
            passphrase=passphrase,
            paper_trading=(connection.account_type == "paper"),
        )

    @staticmethod
    async def test_connection(connection: BrokerConnection) -> tuple[bool, str]:
        try:
            broker = BrokerService.create_broker_from_connection(connection)
            success = await broker.test_connection()
            if success:
                connection.status = "active"
                connection.last_error = ""
            else:
                connection.status = "error"
                connection.last_error = "Connection test failed"
            connection.save()
            return success, connection.last_error
        except Exception as e:
            error_msg = str(e)
            connection.status = "error"
            connection.last_error = error_msg
            connection.save()
            logger.error(f"Broker connection test failed: {e}")
            return False, error_msg

    @staticmethod
    async def sync_portfolio(
        connection: BrokerConnection, sync_type: str = "full"
    ) -> PortfolioSyncLog:
        sync_log = PortfolioSyncLog.objects.create(
            connection=connection,
            sync_type=sync_type,
            status="in_progress",
        )

        try:
            broker = BrokerService.create_broker_from_connection(connection)
            portfolio = await broker.sync_portfolio()

            if sync_type in ("full", "incremental"):
                await BrokerService._sync_positions(
                    connection, portfolio["positions"], sync_log
                )

            if sync_type in ("full", "incremental", "transactions"):
                await BrokerService._sync_transactions(
                    connection, portfolio["transactions"], sync_log
                )

            if sync_type in ("full", "orders"):
                await BrokerService._sync_orders(
                    connection, portfolio["orders"], sync_log
                )

            connection.last_sync_at = datetime.now()
            connection.save()
            sync_log.mark_completed()

        except Exception as e:
            sync_log.mark_failed(str(e))
            logger.error(f"Portfolio sync failed: {e}")

        return sync_log

    @staticmethod
    async def _sync_positions(
        connection: BrokerConnection, positions: list, sync_log: PortfolioSyncLog
    ):
        for pos in positions:
            BrokerPosition.objects.update_or_create(
                connection=connection,
                symbol=pos.symbol,
                external_position_id=pos.external_position_id or pos.symbol,
                defaults={
                    "asset_id": pos.asset_id,
                    "quantity": pos.quantity,
                    "avg_entry_price": pos.avg_entry_price,
                    "current_price": pos.current_price,
                    "market_value": pos.market_value,
                    "unrealized_pl": pos.unrealized_pl,
                    "unrealized_pl_percent": pos.unrealized_pl_percent,
                    "side": pos.side,
                    "cost_basis": pos.cost_basis,
                    "commission": pos.commission,
                },
            )
            sync_log.positions_synced += 1
        sync_log.save()

    @staticmethod
    async def _sync_transactions(
        connection: BrokerConnection, transactions: list, sync_log: PortfolioSyncLog
    ):
        for tx in transactions:
            BrokerTransaction.objects.update_or_create(
                connection=connection,
                external_transaction_id=tx.transaction_id,
                defaults={
                    "transaction_type": tx.transaction_type,
                    "symbol": tx.symbol,
                    "quantity": tx.quantity,
                    "price": tx.price,
                    "total": tx.total,
                    "fee": tx.fee,
                    "currency": tx.currency,
                    "status": tx.status,
                    "executed_at": tx.executed_at,
                    "order_id": tx.order_id,
                },
            )
            sync_log.transactions_synced += 1
        sync_log.save()

    @staticmethod
    async def _sync_orders(
        connection: BrokerConnection, orders: list, sync_log: PortfolioSyncLog
    ):
        for order in orders:
            BrokerOrder.objects.update_or_create(
                connection=connection,
                external_order_id=order.order_id,
                defaults={
                    "symbol": order.symbol,
                    "order_type": order.order_type,
                    "side": order.side,
                    "quantity": order.quantity,
                    "filled_quantity": order.filled_quantity,
                    "limit_price": order.limit_price,
                    "stop_price": order.stop_price,
                    "time_in_force": order.time_in_force,
                    "status": order.status,
                    "submitted_at": order.submitted_at,
                    "filled_at": order.filled_at,
                    "avg_fill_price": order.avg_fill_price,
                    "commission": order.commission,
                },
            )
            sync_log.orders_synced += 1
        sync_log.save()

    @staticmethod
    async def execute_trade(
        connection: BrokerConnection, order_data: Dict[str, Any]
    ) -> BrokerOrder:
        broker = BrokerService.create_broker_from_connection(connection)
        return await broker.place_order(
            symbol=order_data["symbol"],
            order_type=order_data["order_type"],
            side=order_data["side"],
            quantity=Decimal(str(order_data["quantity"])),
            limit_price=Decimal(str(order_data["limit_price"]))
            if order_data.get("limit_price")
            else None,
            stop_price=Decimal(str(order_data["stop_price"]))
            if order_data.get("stop_price")
            else None,
            time_in_force=order_data.get("time_in_force", "day"),
        )

    @staticmethod
    async def cancel_broker_order(connection: BrokerConnection, order_id: str) -> bool:
        broker = BrokerService.create_broker_from_connection(connection)
        return await broker.cancel_order(order_id)

    @staticmethod
    def get_connection_summary(connection: BrokerConnection) -> Dict[str, Any]:
        positions_count = BrokerPosition.objects.filter(connection=connection).count()
        orders_count = BrokerOrder.objects.filter(
            connection=connection,
            status__in=["pending_new", "accepted", "partial_filled"],
        ).count()
        transactions_count = BrokerTransaction.objects.filter(
            connection=connection
        ).count()

        return {
            "id": str(connection.id),
            "broker": connection.broker,
            "account_id": connection.account_id,
            "account_name": connection.account_name,
            "status": connection.status,
            "last_sync_at": connection.last_sync_at,
            "positions_count": positions_count,
            "open_orders_count": orders_count,
            "transactions_count": transactions_count,
        }
