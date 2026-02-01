from ninja import Router
from django.http import JsonResponse
from typing import List
from pydantic import BaseModel
from datetime import datetime

from brokers.models import (
    BrokerConnection,
    BrokerPosition,
    BrokerTransaction,
    BrokerOrder,
)
from brokers.services.broker_service import BrokerService, EncryptionService

router = Router()


class ConnectionCreateIn(BaseModel):
    broker: str
    account_type: str
    api_key: str
    api_secret: str
    passphrase: str = None
    account_name: str = ""


class ConnectionOut(BaseModel):
    id: str
    broker: str
    account_id: str
    account_name: str
    account_type: str
    status: str
    last_sync_at: datetime = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class OrderCreateIn(BaseModel):
    symbol: str
    order_type: str
    side: str
    quantity: float
    limit_price: float = None
    stop_price: float = None
    time_in_force: str = "day"


@router.post("/connections")
async def create_connection(request, data: ConnectionCreateIn):
    user = request.user
    api_key_enc = EncryptionService.encrypt(data.api_key.encode())
    api_secret_enc = EncryptionService.encrypt(data.api_secret.encode())
    passphrase_enc = None
    if data.passphrase:
        passphrase_enc = EncryptionService.encrypt(data.passphrase.encode())

    connection = BrokerConnection.objects.create(
        user=user,
        broker=data.broker,
        account_type=data.account_type,
        account_name=data.account_name or f"{data.broker} {data.account_type}",
        api_key_encrypted=api_key_enc,
        api_secret_encrypted=api_secret_enc,
        passphrase_encrypted=passphrase_enc,
    )

    success, error = await BrokerService.test_connection(connection)
    return {
        "success": success,
        "error": error,
        "connection": {"id": str(connection.id), "status": connection.status},
    }


@router.get("/connections", response=List[ConnectionOut])
def list_connections(request):
    user = request.user
    connections = BrokerConnection.objects.filter(user=user, deleted_at__isnull=True)
    return [
        {
            "id": str(c.id),
            "broker": c.broker,
            "account_id": c.account_id,
            "account_name": c.account_name,
            "account_type": c.account_type,
            "status": c.status,
            "last_sync_at": c.last_sync_at,
        }
        for c in connections
    ]


@router.post("/connections/{connection_id}/sync")
async def sync_connection(request, connection_id: str):
    user = request.user
    try:
        connection = BrokerConnection.objects.get(
            id=connection_id, user=user, deleted_at__isnull=True
        )
    except BrokerConnection.DoesNotExist:
        return JsonResponse({"error": "Connection not found"}, status=404)

    sync_log = await BrokerService.sync_portfolio(connection, sync_type="full")
    return {
        "sync_id": str(sync_log.id),
        "status": sync_log.status,
        "positions_synced": sync_log.positions_synced,
        "transactions_synced": sync_log.transactions_synced,
        "orders_synced": sync_log.orders_synced,
    }


@router.post("/connections/{connection_id}/test")
async def test_connection(request, connection_id: str):
    user = request.user
    try:
        connection = BrokerConnection.objects.get(
            id=connection_id, user=user, deleted_at__isnull=True
        )
    except BrokerConnection.DoesNotExist:
        return JsonResponse({"error": "Connection not found"}, status=404)

    success, error = await BrokerService.test_connection(connection)
    return {"success": success, "error": error}


@router.get("/connections/{connection_id}/positions")
def get_positions(request, connection_id: str):
    user = request.user
    try:
        connection = BrokerConnection.objects.get(
            id=connection_id, user=user, deleted_at__isnull=True
        )
    except BrokerConnection.DoesNotExist:
        return JsonResponse({"error": "Connection not found"}, status=404)

    positions = BrokerPosition.objects.filter(
        connection=connection, deleted_at__isnull=True
    )
    return [
        {
            "symbol": p.symbol,
            "quantity": str(p.quantity),
            "avg_entry_price": str(p.avg_entry_price),
            "current_price": str(p.current_price),
            "market_value": str(p.market_value),
            "unrealized_pl": str(p.unrealized_pl),
            "unrealized_pl_percent": str(p.unrealized_pl_percent),
            "side": p.side,
        }
        for p in positions
    ]


@router.get("/connections/{connection_id}/orders")
def get_orders(request, connection_id: str):
    user = request.user
    try:
        connection = BrokerConnection.objects.get(
            id=connection_id, user=user, deleted_at__isnull=True
        )
    except BrokerConnection.DoesNotExist:
        return JsonResponse({"error": "Connection not found"}, status=404)

    orders = BrokerOrder.objects.filter(
        connection=connection, deleted_at__isnull=True
    ).order_by("-submitted_at")[:50]
    return [
        {
            "order_id": o.external_order_id,
            "symbol": o.symbol,
            "order_type": o.order_type,
            "side": o.side,
            "quantity": str(o.quantity),
            "filled_quantity": str(o.filled_quantity),
            "status": o.status,
            "submitted_at": o.submitted_at.isoformat() if o.submitted_at else None,
        }
        for o in orders
    ]


@router.get("/connections/{connection_id}/transactions")
def get_transactions(request, connection_id: str):
    user = request.user
    try:
        connection = BrokerConnection.objects.get(
            id=connection_id, user=user, deleted_at__isnull=True
        )
    except BrokerConnection.DoesNotExist:
        return JsonResponse({"error": "Connection not found"}, status=404)

    transactions = BrokerTransaction.objects.filter(
        connection=connection, deleted_at__isnull=True
    ).order_by("-executed_at")[:100]
    return [
        {
            "transaction_id": tx.external_transaction_id,
            "type": tx.transaction_type,
            "symbol": tx.symbol,
            "quantity": str(tx.quantity) if tx.quantity else None,
            "price": str(tx.price) if tx.price else None,
            "total": str(tx.total) if tx.total else None,
            "executed_at": tx.executed_at.isoformat() if tx.executed_at else None,
        }
        for tx in transactions
    ]


@router.post("/connections/{connection_id}/orders")
async def place_order(request, connection_id: str, data: OrderCreateIn):
    user = request.user
    try:
        connection = BrokerConnection.objects.get(
            id=connection_id, user=user, deleted_at__isnull=True
        )
    except BrokerConnection.DoesNotExist:
        return JsonResponse({"error": "Connection not found"}, status=404)

    order_data = data.model_dump()
    try:
        order = await BrokerService.execute_trade(connection, order_data)
        return {
            "order_id": order.order_id,
            "symbol": order.symbol,
            "status": order.status,
            "submitted_at": order.submitted_at.isoformat()
            if order.submitted_at
            else None,
        }
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
        return JsonResponse({"error": str(e)}, status=400)


@router.delete("/connections/{connection_id}/orders/{order_id}")
async def cancel_order(request, connection_id: str, order_id: str):
    user = request.user
    try:
        connection = BrokerConnection.objects.get(
            id=connection_id, user=user, deleted_at__isnull=True
        )
    except BrokerConnection.DoesNotExist:
        return JsonResponse({"error": "Connection not found"}, status=404)

    success = await BrokerService.cancel_broker_order(connection, order_id)
    return {"success": success}


@router.delete("/connections/{connection_id}")
def delete_connection(request, connection_id: str):
    user = request.user
    try:
        connection = BrokerConnection.objects.get(id=connection_id, user=user)
        connection.soft_delete()
        return {"success": True}
    except BrokerConnection.DoesNotExist:
        return JsonResponse({"error": "Connection not found"}, status=404)
