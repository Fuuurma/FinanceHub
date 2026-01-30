# C-030: Broker API Integration & Portfolio Sync

**Priority:** P1 - HIGH  
**Assigned to:** Backend Coder  
**Estimated Time:** 14-18 hours  
**Dependencies:** C-025 (CSV Bulk Import), C-011 (Portfolio Analytics)  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement broker API integration system to automatically import portfolios and transactions from major brokerages (Alpaca, Interactive Brokers, Coinbase, etc.) with real-time synchronization and reconciliation.

---

## 📊 FEATURE DESCRIPTION

**From Features Specification (Section 4.1 - Portfolio Tracking):**

- Broker API import (where available)
- Multiple portfolio support
- Automatic dividend tracking
- Cost basis tracking (FIFO, LIFO, specific lot)
- Real-time portfolio value

---

## ✅ CURRENT STATE

**What exists:**
- Manual portfolio entry (C-025)
- CSV bulk import (C-025)
- Basic portfolio tracking

**What's missing:**
- Broker API connections
- Automatic portfolio sync
- Transaction reconciliation
- Multi-broker support
- API credential management

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 1: Database Models** (2-3 hours)

**Create `apps/backend/src/investments/models/broker_integration.py`:**

```python
from django.db import models
from django.contrib.auth import get_user_model
from .portfolio import Portfolio

User = get_user_model()

class BrokerConnection(models.Model):
    """User's broker API connections"""
    
    BROKER_CHOICES = [
        ('alpaca', 'Alpaca'),
        ('interactive_brokers', 'Interactive Brokers'),
        ('coinbase', 'Coinbase'),
        ('binance', 'Binance'),
        ('kraken', 'Kraken'),
        ('td_ameritrade', 'TD Ameritrade'),
        ('fidelity', 'Fidelity'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('error', 'Error'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ]
    
    # User and broker
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='broker_connections')
    broker = models.CharField(max_length=50, choices=BROKER_CHOICES)
    
    # Connection details (encrypted in production)
    api_key = models.CharField(max_length=500)  # Encrypted
    api_secret = models.CharField(max_length=500)  # Encrypted
    access_token = models.CharField(max_length=500, blank=True)  # For OAuth
    refresh_token = models.CharField(max_length=500, blank=True)
    
    # Connection settings
    is_paper_trading = models.BooleanField(default=False)
    environment = models.CharField(max_length=20, default='live')  # live, paper
    sync_enabled = models.BooleanField(default=True)
    
    # Sync settings
    sync_interval = models.IntegerField(default=3600)  # Seconds between syncs
    sync_positions = models.BooleanField(default=True)
    sync_transactions = models.BooleanField(default=True)
    sync_orders = models.BooleanField(default=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_sync_status = models.CharField(max_length=20, null=True, blank=True)
    last_sync_message = models.TextField(blank=True)
    error_count = models.IntegerField(default=0)
    
    # Account info from broker
    broker_account_id = models.CharField(max_length=100, blank=True)
    broker_account_type = models.CharField(max_length=50, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'broker']),
            models.Index(fields=['status']),
            models.Index(fields=['last_sync_at']),
        ]
        unique_together = [['user', 'broker']]

class PortfolioSyncLog(models.Model):
    """Log of portfolio synchronization attempts"""
    
    SYNC_TYPE_CHOICES = [
        ('full', 'Full Sync'),
        ('positions', 'Positions Only'),
        ('transactions', 'Transactions Only'),
        ('orders', 'Orders Only'),
    ]
    
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('partial', 'Partial Success'),
        ('failed', 'Failed'),
    ]
    
    # References
    connection = models.ForeignKey(BrokerConnection, on_delete=models.CASCADE, related_name='sync_logs')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='sync_logs')
    
    # Sync details
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True)
    
    # Results
    positions_added = models.IntegerField(default=0)
    positions_updated = models.IntegerField(default=0)
    positions_removed = models.IntegerField(default=0)
    transactions_added = models.IntegerField(default=0)
    orders_synced = models.IntegerField(default=0)
    
    # Error details
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['connection', '-started_at']),
            models.Index(fields=['portfolio', '-started_at']),
        ]

class BrokerPosition(models.Model):
    """Positions synced from broker"""
    
    connection = models.ForeignKey(BrokerConnection, on_delete=models.CASCADE, related_name='positions')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='broker_positions')
    
    # Asset
    asset_id = models.IntegerField()
    symbol = models.CharField(max_length=20)
    
    # Position details
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    avg_entry_price = models.DecimalField(max_digits=20, decimal_places=6)
    current_price = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    market_value = models.DecimalField(max_digits=20, decimal_places=2)
    cost_basis = models.DecimalField(max_digits=20, decimal_places=2)
    
    # P&L
    unrealized_pnl = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    unrealized_pnl_pct = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    
    # Broker-specific data
    broker_position_id = models.CharField(max_length=100, blank=True)
    asset_type = models.CharField(max_length=20, blank=True)  # stock, option, crypto, etc.
    exchange = models.CharField(max_length=50, blank=True)
    
    # Timestamps
    synced_at = models.DateTimeField(auto_now=True)
    broker_timestamp = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['connection', 'symbol']),
            models.Index(fields=['portfolio', 'symbol']),
            models.Index(fields=['-synced_at']),
        ]
        unique_together = [['connection', 'symbol']]

class BrokerTransaction(models.Model):
    """Transactions synced from broker"""
    
    TRANSACTION_TYPE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
        ('dividend', 'Dividend'),
        ('split', 'Stock Split'),
        ('transfer', 'Transfer'),
        ('fee', 'Fee'),
        ('interest', 'Interest'),
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    ]
    
    connection = models.ForeignKey(BrokerConnection, on_delete=models.CASCADE, related_name='transactions')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='broker_transactions')
    
    # Asset
    asset_id = models.IntegerField(null=True)
    symbol = models.CharField(max_length=20, blank=True)
    
    # Transaction details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=20, decimal_places=8, null=True)
    price = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    total_amount = models.DecimalField(max_digits=20, decimal_places=2)
    
    # Fees and commissions
    commission = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    fees = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    
    # Timestamps
    transaction_date = models.DateTimeField()
    settled_date = models.DateTimeField(null=True, blank=True)
    synced_at = models.DateTimeField(auto_now_add=True)
    
    # Broker-specific
    broker_transaction_id = models.CharField(max_length=100, unique=True)
    order_id = models.CharField(max_length=100, blank=True)
    
    # Reconciliation
    reconciled = models.BooleanField(default=False)
    local_transaction_id = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['connection', 'transaction_date']),
            models.Index(fields=['portfolio', 'transaction_date']),
            models.Index(fields=['broker_transaction_id']),
        ]

class BrokerOrder(models.Model):
    """Active orders from broker"""
    
    SIDE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('open', 'Open'),
        ('filled', 'Filled'),
        ('partially_filled', 'Partially Filled'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    TYPE_CHOICES = [
        ('market', 'Market'),
        ('limit', 'Limit'),
        ('stop', 'Stop'),
        ('stop_limit', 'Stop Limit'),
        ('trailing_stop', 'Trailing Stop'),
    ]
    
    connection = models.ForeignKey(BrokerConnection, on_delete=models.CASCADE, related_name='orders')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='broker_orders')
    
    # Asset
    asset_id = models.IntegerField()
    symbol = models.CharField(max_length=20)
    
    # Order details
    side = models.CharField(max_length=10, choices=SIDE_CHOICES)
    order_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    filled_quantity = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    
    # Price
    limit_price = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    stop_price = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    avg_fill_price = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField()
    filled_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Broker-specific
    broker_order_id = models.CharField(max_length=100, unique=True)
    
    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['connection', 'status']),
            models.Index(fields=['portfolio', '-submitted_at']),
        ]
```

---

### **Phase 2: Broker Integration Service** (6-7 hours)

**Create `apps/backend/src/investments/services/broker_service.py`:**

```python
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from cryptography.fernet import Fernet
import requests
import json

from investments.models.broker_integration import (
    BrokerConnection, PortfolioSyncLog, BrokerPosition,
    BrokerTransaction, BrokerOrder
)
from investments.models.portfolio import Portfolio, PortfolioPosition
from investments.models.asset import Asset

class BrokerIntegrationService:
    
    def __init__(self):
        # Initialize encryption for API keys
        self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
        
        # Broker API base URLs
        self.broker_urls = {
            'alpaca': 'https://api.alpaca.markets',
            'coinbase': 'https://api.coinbase.com',
            'binance': 'https://api.binance.com',
            'kraken': 'https://api.kraken.com',
        }
    
    def _encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    @transaction.atomic
    def create_connection(
        self,
        user_id: int,
        broker: str,
        api_key: str,
        api_secret: str,
        is_paper_trading: bool = False
    ) -> Dict:
        """Create new broker connection"""
        
        # Validate credentials
        is_valid, account_id = self._validate_credentials(broker, api_key, api_secret, is_paper_trading)
        
        if not is_valid:
            return {'error': 'Invalid credentials'}
        
        # Create connection
        connection = BrokerConnection.objects.create(
            user_id=user_id,
            broker=broker,
            api_key=self._encrypt(api_key),
            api_secret=self._encrypt(api_secret),
            is_paper_trading=is_paper_trading,
            broker_account_id=account_id,
            status='active'
        )
        
        # Create portfolio for this connection
        portfolio = Portfolio.objects.create(
            user_id=user_id,
            name=f"{broker.title()} Portfolio",
            is_synced=True,
            broker_connection=connection
        )
        
        # Initial sync
        self.sync_portfolio(connection.id)
        
        return {
            'connection_id': connection.id,
            'portfolio_id': portfolio.id,
            'broker_account_id': account_id
        }
    
    def _validate_credentials(
        self,
        broker: str,
        api_key: str,
        api_secret: str,
        is_paper_trading: bool
    ) -> Tuple[bool, Optional[str]]:
        """Validate broker API credentials"""
        
        try:
            if broker == 'alpaca':
                return self._validate_alpaca(api_key, api_secret, is_paper_trading)
            elif broker == 'coinbase':
                return self._validate_coinbase(api_key, api_secret)
            elif broker == 'binance':
                return self._validate_binance(api_key, api_secret)
            # Add other brokers...
        except Exception as e:
            print(f"Credential validation error: {e}")
            return False, None
        
        return False, None
    
    def _validate_alpaca(
        self,
        api_key: str,
        api_secret: str,
        is_paper_trading: bool
    ) -> Tuple[bool, Optional[str]]:
        """Validate Alpaca credentials"""
        base_url = 'https://paper-api.alpaca.markets' if is_paper_trading else 'https://api.alpaca.markets'
        
        response = requests.get(
            f'{base_url}/v2/account',
            headers={
                'APCA-API-KEY-ID': api_key,
                'APCA-API-SECRET-KEY': api_secret
            }
        )
        
        if response.status_code == 200:
            account_data = response.json()
            account_id = account_data.get('id')
            return True, account_id
        
        return False, None
    
    def _validate_coinbase(self, api_key: str, api_secret: str) -> Tuple[bool, Optional[str]]:
        """Validate Coinbase credentials"""
        # Coinbase API validation
        # Similar implementation
        pass
    
    def _validate_binance(self, api_key: str, api_secret: str) -> Tuple[bool, Optional[str]]:
        """Validate Binance credentials"""
        # Binance API validation
        pass
    
    @transaction.atomic
    def sync_portfolio(
        self,
        connection_id: int,
        sync_type: str = 'full'
    ) -> Dict:
        """Sync portfolio from broker"""
        
        connection = BrokerConnection.objects.get(id=connection_id)
        
        # Create sync log
        sync_log = PortfolioSyncLog.objects.create(
            connection=connection,
            portfolio_id=connection.user.portfolios.filter(broker_connection=connection).first().id,
            sync_type=sync_type,
            status='in_progress'
        )
        
        try:
            start_time = timezone.now()
            
            if sync_type in ['full', 'positions']:
                positions_added, positions_updated, positions_removed = \
                    self._sync_positions(connection, sync_log)
            
            if sync_type in ['full', 'transactions']:
                transactions_added = self._sync_transactions(connection, sync_log)
            
            if sync_type in ['full', 'orders']:
                orders_synced = self._sync_orders(connection, sync_log)
            
            # Update sync log
            sync_log.completed_at = timezone.now()
            sync_log.duration_seconds = int((sync_log.completed_at - start_time).total_seconds())
            sync_log.status = 'success'
            sync_log.save()
            
            # Update connection
            connection.last_sync_at = timezone.now()
            connection.last_sync_status = 'success'
            connection.error_count = 0
            connection.save()
            
            return {
                'sync_log_id': sync_log.id,
                'status': 'success',
                'positions_added': positions_added,
                'transactions_added': transactions_added
            }
            
        except Exception as e:
            sync_log.completed_at = timezone.now()
            sync_log.status = 'failed'
            sync_log.error_message = str(e)
            sync_log.save()
            
            connection.last_sync_status = 'error'
            connection.error_count += 1
            if connection.error_count >= 5:
                connection.status = 'error'
            connection.save()
            
            raise
    
    def _sync_positions(
        self,
        connection: BrokerConnection,
        sync_log: PortfolioSyncLog
    ) -> Tuple[int, int, int]:
        """Sync positions from broker"""
        
        if connection.broker == 'alpaca':
            positions = self._fetch_alpaca_positions(connection)
        elif connection.broker == 'coinbase':
            positions = self._fetch_coinbase_positions(connection)
        # Add other brokers...
        else:
            positions = []
        
        added = 0
        updated = 0
        removed = 0
        
        portfolio = sync_log.portfolio
        
        # Get existing positions
        existing_positions = {
            bp.symbol: bp 
            for bp in BrokerPosition.objects.filter(connection=connection)
        }
        
        # Process positions
        for pos_data in positions:
            symbol = pos_data['symbol']
            
            # Get or create asset
            asset = Asset.objects.filter(symbol=symbol).first()
            if not asset:
                # Create asset
                asset = Asset.objects.create(
                    symbol=symbol,
                    name=pos_data.get('name', symbol),
                    asset_type=pos_data.get('asset_type', 'stock'),
                    exchange=pos_data.get('exchange', 'UNKNOWN'),
                )
            
            # Update or create position
            if symbol in existing_positions:
                # Update existing
                broker_pos = existing_positions[symbol]
                broker_pos.quantity = Decimal(str(pos_data['quantity']))
                broker_pos.avg_entry_price = Decimal(str(pos_data['avg_entry_price']))
                broker_pos.market_value = Decimal(str(pos_data['market_value']))
                broker_pos.cost_basis = Decimal(str(pos_data['cost_basis']))
                broker_pos.unrealized_pnl = Decimal(str(pos_data.get('unrealized_pnl', 0)))
                broker_pos.unrealized_pnl_pct = Decimal(str(pos_data.get('unrealized_pnl_pct', 0)))
                broker_pos.save()
                updated += 1
            else:
                # Create new
                BrokerPosition.objects.create(
                    connection=connection,
                    portfolio=portfolio,
                    asset_id=asset.id,
                    symbol=symbol,
                    quantity=Decimal(str(pos_data['quantity'])),
                    avg_entry_price=Decimal(str(pos_data['avg_entry_price'])),
                    market_value=Decimal(str(pos_data['market_value'])),
                    cost_basis=Decimal(str(pos_data['cost_basis'])),
                    unrealized_pnl=Decimal(str(pos_data.get('unrealized_pnl', 0))),
                    unrealized_pnl_pct=Decimal(str(pos_data.get('unrealized_pnl_pct', 0))),
                    asset_type=pos_data.get('asset_type', 'stock'),
                    exchange=pos_data.get('exchange', ''),
                )
                added += 1
        
        # Remove closed positions
        broker_symbols = set(p['symbol'] for p in positions)
        for symbol, broker_pos in existing_positions.items():
            if symbol not in broker_symbols and broker_pos.quantity == 0:
                broker_pos.delete()
                removed += 1
        
        # Update sync log
        sync_log.positions_added = added
        sync_log.positions_updated = updated
        sync_log.positions_removed = removed
        sync_log.save()
        
        return added, updated, removed
    
    def _fetch_alpaca_positions(self, connection: BrokerConnection) -> List[Dict]:
        """Fetch positions from Alpaca"""
        api_key = self._decrypt(connection.api_key)
        api_secret = self._decrypt(connection.api_secret)
        
        base_url = 'https://paper-api.alpaca.markets' if connection.is_paper_trading else 'https://api.alpaca.markets'
        
        response = requests.get(
            f'{base_url}/v2/positions',
            headers={
                'APCA-API-KEY-ID': api_key,
                'APCA-API-SECRET-KEY': api_secret
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Alpaca API error: {response.status_code}")
        
        positions = []
        for pos in response.json():
            positions.append({
                'symbol': pos['symbol'],
                'quantity': abs(float(pos['qty'])),
                'avg_entry_price': float(pos['avg_entry_price']),
                'market_value': float(pos['market_value']),
                'cost_basis': float(pos['cost_basis']),
                'unrealized_pnl': float(pos['unrealized_pl']),
                'unrealized_pnl_pct': float(pos['unrealized_plpc']) * 100,
                'asset_type': 'stock',
                'exchange': 'NASDAQ',
            })
        
        return positions
    
    def _fetch_coinbase_positions(self, connection: BrokerConnection) -> List[Dict]:
        """Fetch positions from Coinbase"""
        # Coinbase API implementation
        pass
    
    def _sync_transactions(
        self,
        connection: BrokerConnection,
        sync_log: PortfolioSyncLog
    ) -> int:
        """Sync transactions from broker"""
        # Similar implementation to positions
        pass
    
    def _sync_orders(
        self,
        connection: BrokerConnection,
        sync_log: PortfolioSyncLog
    ) -> int:
        """Sync orders from broker"""
        # Similar implementation
        pass
    
    def get_connections(self, user_id: int) -> List[Dict]:
        """Get user's broker connections"""
        connections = BrokerConnection.objects.filter(user_id=user_id)
        
        return [
            {
                'id': c.id,
                'broker': c.broker,
                'broker_account_id': c.broker_account_id,
                'is_paper_trading': c.is_paper_trading,
                'status': c.status,
                'sync_enabled': c.sync_enabled,
                'last_sync_at': c.last_sync_at.isoformat() if c.last_sync_at else None,
                'last_sync_status': c.last_sync_status,
                'error_count': c.error_count,
            }
            for c in connections
        ]
    
    def get_sync_logs(self, connection_id: int, limit: int = 20) -> List[Dict]:
        """Get sync logs for connection"""
        logs = PortfolioSyncLog.objects.filter(
            connection_id=connection_id
        ).order_by('-started_at')[:limit]
        
        return [
            {
                'id': log.id,
                'sync_type': log.sync_type,
                'status': log.status,
                'started_at': log.started_at.isoformat(),
                'completed_at': log.completed_at.isoformat() if log.completed_at else None,
                'duration_seconds': log.duration_seconds,
                'positions_added': log.positions_added,
                'transactions_added': log.transactions_added,
                'error_message': log.error_message,
            }
            for log in logs
        ]
    
    @transaction.atomic
    def disconnect(self, connection_id: int):
        """Disconnect broker connection"""
        connection = BrokerConnection.objects.get(id=connection_id)
        connection.status = 'revoked'
        connection.sync_enabled = False
        connection.save()
```

---

### **Phase 3: API Endpoints** (3-4 hours)

**Create `apps/backend/src/api/broker_integration.py`:**

```python
from ninja import Router, Schema
from investments.services.broker_service import BrokerIntegrationService

router = Router(tags=['broker_integration'])
broker_service = BrokerIntegrationService()

class BrokerConnectionSchema(Schema):
    broker: str
    api_key: str
    api_secret: str
    is_paper_trading: bool = False

@router.post("/broker/connect")
def connect_broker(request, data: BrokerConnectionSchema):
    """Connect to broker account"""
    result = broker_service.create_connection(
        user_id=request.auth.id,
        broker=data.broker,
        api_key=data.api_key,
        api_secret=data.api_secret,
        is_paper_trading=data.is_paper_trading
    )
    
    return result

@router.get("/broker/connections")
def get_connections(request):
    """Get user's broker connections"""
    return broker_service.get_connections(request.auth.id)

@router.post("/broker/{connection_id}/sync")
def sync_portfolio(request, connection_id: int, sync_type: str = 'full'):
    """Sync portfolio from broker"""
    result = broker_service.sync_portfolio(connection_id, sync_type)
    return result

@router.get("/broker/{connection_id}/sync-logs")
def get_sync_logs(request, connection_id: int, limit: int = 20):
    """Get sync logs"""
    return broker_service.get_sync_logs(connection_id, limit)

@router.post("/broker/{connection_id}/disconnect")
def disconnect_broker(request, connection_id: int):
    """Disconnect broker account"""
    broker_service.disconnect(connection_id)
    return {"status": "disconnected"}

@router.get("/broker/{connection_id}/positions")
def get_broker_positions(request, connection_id: int):
    """Get positions from broker"""
    from investments.models.broker_integration import BrokerPosition
    
    positions = BrokerPosition.objects.filter(connection_id=connection_id)
    
    return [
        {
            'symbol': p.symbol,
            'quantity': float(p.quantity),
            'avg_entry_price': float(p.avg_entry_price),
            'market_value': float(p.market_value),
            'unrealized_pnl': float(p.unrealized_pnl) if p.unrealized_pnl else None,
            'unrealized_pnl_pct': float(p.unrealized_pnl_pct) if p.unrealized_pnl_pct else None,
        }
        for p in positions
    ]
```

---

### **Phase 4: Scheduled Sync Tasks** (2-3 hours)

**Create Dramatiq tasks for automatic sync:**

```python
# apps/backend/src/investments/tasks/broker_sync_tasks.py
import dramatiq
from investments.services.broker_service import BrokerIntegrationService

@dramatiq.actor
def sync_all_connections():
    """Sync all active broker connections"""
    from investments.models.broker_integration import BrokerConnection
    
    active_connections = BrokerConnection.objects.filter(
        status='active',
        sync_enabled=True
    )
    
    service = BrokerIntegrationService()
    
    for connection in active_connections:
        # Check if sync is due
        if connection.last_sync_at is None or \
           (timezone.now() - connection.last_sync_at).total_seconds() >= connection.sync_interval:
            try:
                service.sync_portfolio(connection.id)
            except Exception as e:
                print(f"Sync failed for connection {connection.id}: {e}")

@dramatiq.actor
def sync_connection(connection_id: int):
    """Sync specific connection"""
    service = BrokerIntegrationService()
    service.sync_portfolio(connection_id)
```

---

## 📋 DELIVERABLES

- [ ] BrokerConnection, PortfolioSyncLog models
- [ ] BrokerPosition, BrokerTransaction, BrokerOrder models
- [ ] BrokerIntegrationService with 10+ methods
- [ ] Support for 3+ brokers (Alpaca, Coinbase, Binance)
- [ ] 6 API endpoints
- [ ] Automatic sync scheduling
- [ ] API encryption for credentials
- [ ] Database migrations
- [ ] Unit tests

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Users can connect broker accounts securely
- [ ] API credentials encrypted and stored
- [ ] Portfolio sync works for Alpaca (paper and live)
- [ ] Positions sync correctly
- [ ] Transactions sync correctly
- [ ] Orders sync correctly
- [ ] Automatic sync on schedule
- [ ] Sync logs track all activity
- [ ] Error handling and retry logic
- [ ] All tests passing

---

## 📊 SUCCESS METRICS

- Connection setup time <30 seconds
- Full sync time <2 minutes for typical portfolio
- Sync success rate >95%
- Support for 1000+ concurrent connections
- API encryption/decryption <100ms
- Automatic sync reliability >99%

---

**Task created:** January 30, 2026  
**Task file:** tasks/coders/030-broker-api-integration.md
