import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import threading

from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class WebSocketConnectionMetrics:
    """
    Singleton class for tracking WebSocket connection metrics.
    
    Tracks:
    - Active connections per user
    - Subscription counts per data type
    - Connection/disconnection events
    - Error tracking
    - Activity timestamps
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._connections: Dict[str, Dict[str, Any]] = {}
            self._subscriptions: Dict[str, Set[str]] = defaultdict(set)
            self._errors: List[Dict[str, Any]] = []
            self._max_error_entries = 1000
            logger.info("WebSocketConnectionMetrics initialized")
    
    def record_connection(self, user_id: str, channel_name: str, user_agent: Optional[str] = None):
        """
        Record a new WebSocket connection.
        
        Args:
            user_id: User identifier (or 'anonymous')
            channel_name: WebSocket channel name
            user_agent: Client user agent string
        """
        try:
            connection_info = {
                'channel_name': channel_name,
                'user_agent': user_agent,
                'connected_at': datetime.utcnow().isoformat(),
                'subscriptions': [],
                'last_activity': datetime.utcnow().isoformat()
            }
            
            self._connections[channel_name] = connection_info
            logger.info(f"Recorded connection for user {user_id}: {channel_name}")
        except Exception as e:
            logger.error(f"Error recording connection: {e}")
    
    def record_disconnection(self, user_id: str):
        """
        Record a WebSocket disconnection.
        
        Args:
            user_id: User identifier
        """
        try:
            disconnected_at = datetime.utcnow().isoformat()
            logger.info(f"Recorded disconnection for user {user_id} at {disconnected_at}")
        except Exception as e:
            logger.error(f"Error recording disconnection: {e}")
    
    def record_error(self, error: str, context: Optional[Dict[str, Any]] = None):
        """
        Record a WebSocket-related error.
        
        Args:
            error: Error message
            context: Additional error context
        """
        try:
            error_entry = {
                'error': error,
                'context': context or {},
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self._errors.append(error_entry)
            
            # Keep error list manageable
            if len(self._errors) > self._max_error_entries:
                self._errors = self._errors[-self._max_error_entries:]
            
            logger.error(f"Recorded error: {error}")
        except Exception as e:
            logger.error(f"Error recording error: {e}")
    
    def update_activity(self, channel_name: str):
        """
        Update the last activity timestamp for a connection.
        
        Args:
            channel_name: WebSocket channel name
        """
        try:
            if channel_name in self._connections:
                self._connections[channel_name]['last_activity'] = datetime.utcnow().isoformat()
        except Exception as e:
            logger.error(f"Error updating activity: {e}")
    
    def add_subscription(self, user_id: str, data_type: str, symbol: str):
        """
        Add a subscription to track.
        
        Args:
            user_id: User identifier
            data_type: Type of data (price, trade, orderbook, etc.)
            symbol: Trading symbol
        """
        try:
            subscription_key = f"{data_type}:{symbol}"
            self._subscriptions[user_id].add(subscription_key)
            logger.debug(f"Added subscription for {user_id}: {subscription_key}")
        except Exception as e:
            logger.error(f"Error adding subscription: {e}")
    
    def remove_subscription(self, user_id: str, data_type: str, symbol: str):
        """
        Remove a subscription from tracking.
        
        Args:
            user_id: User identifier
            data_type: Type of data
            symbol: Trading symbol
        """
        try:
            subscription_key = f"{data_type}:{symbol}"
            self._subscriptions[user_id].discard(subscription_key)
            logger.debug(f"Removed subscription for {user_id}: {subscription_key}")
        except Exception as e:
            logger.error(f"Error removing subscription: {e}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all metrics.
        
        Returns:
            Dictionary with metrics summary
        """
        try:
            active_connections = len(self._connections)
            total_subscriptions = sum(len(subs) for subs in self._subscriptions.values())
            unique_users = len(self._subscriptions)
            recent_errors = [
                err for err in self._errors[-10:]
                if datetime.fromisoformat(err['timestamp']) > datetime.utcnow() - timedelta(hours=1)
            ]
            
            return {
                'active_connections': active_connections,
                'total_subscriptions': total_subscriptions,
                'unique_users': unique_users,
                'recent_errors_count': len(recent_errors),
                'total_errors': len(self._errors),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting metrics summary: {e}")
            return {}
    
    def get_connection_info(self, user_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a user's connections.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with connection details
        """
        try:
            user_connections = []
            user_subscriptions = list(self._subscriptions.get(user_id, set()))
            
            for channel_name, conn_info in self._connections.items():
                if conn_info.get('user_id') == user_id:
                    user_connections.append({
                        'channel_name': channel_name,
                        'connected_at': conn_info['connected_at'],
                        'last_activity': conn_info['last_activity'],
                        'subscriptions': conn_info['subscriptions']
                    })
            
            return {
                'user_id': user_id,
                'connections': user_connections,
                'subscriptions': user_subscriptions,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting connection info: {e}")
            return {}
    
    def cleanup_old_records(self, hours: int = 24):
        """
        Clean up connection records older than specified hours.
        
        Args:
            hours: Number of hours to keep records
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            to_remove = []
            
            for channel_name, conn_info in self._connections.items():
                last_activity = datetime.fromisoformat(conn_info['last_activity'])
                if last_activity < cutoff_time:
                    to_remove.append(channel_name)
            
            for channel_name in to_remove:
                del self._connections[channel_name]
                logger.info(f"Cleaned up old connection: {channel_name}")
            
            if to_remove:
                logger.info(f"Cleaned up {len(to_remove)} old connection records")
        except Exception as e:
            logger.error(f"Error cleaning up old records: {e}")
    
    def get_all_connections(self) -> List[Dict[str, Any]]:
        """
        Get all active connections.
        
        Returns:
            List of connection dictionaries
        """
        try:
            connections = []
            for channel_name, conn_info in self._connections.items():
                connections.append({
                    'channel_name': channel_name,
                    'connected_at': conn_info['connected_at'],
                    'last_activity': conn_info['last_activity'],
                    'subscriptions': conn_info['subscriptions'],
                    'user_agent': conn_info.get('user_agent')
                })
            return connections
        except Exception as e:
            logger.error(f"Error getting all connections: {e}")
            return []


def get_websocket_metrics() -> Optional[WebSocketConnectionMetrics]:
    """
    Get the singleton instance of WebSocketConnectionMetrics.
    
    Returns:
        WebSocketConnectionMetrics instance or None on error
    """
    try:
        return WebSocketConnectionMetrics()
    except Exception as e:
        logger.error(f"Error getting websocket metrics: {e}")
        return None
