from typing import Dict, Any
from ninja import Router
from utils.services.websocket_monitoring import get_websocket_metrics

router = Router(tags=["Health"])


@router.get("/websockets", response=Dict[str, Any])
def get_websocket_health(request) -> Dict[str, Any]:
    """
    Get WebSocket connection health metrics summary.
    
    Returns:
        Dictionary with overall WebSocket health metrics:
        - active_connections: Number of currently active WebSocket connections
        - total_subscriptions: Total number of active subscriptions across all users
        - unique_users: Number of unique users with active connections
        - recent_errors_count: Number of errors in the last hour
        - total_errors: Total number of recorded errors
        - timestamp: Current timestamp
    """
    try:
        metrics = get_websocket_metrics()
        if metrics:
            return metrics.get_metrics_summary()
        return {
            'active_connections': 0,
            'total_subscriptions': 0,
            'unique_users': 0,
            'recent_errors_count': 0,
            'total_errors': 0,
            'timestamp': None,
            'error': 'Metrics service unavailable'
        }
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        return {
            'active_connections': 0,
            'total_subscriptions': 0,
            'unique_users': 0,
            'recent_errors_count': 0,
            'total_errors': 0,
            'timestamp': None,
            'error': str(e)
        }


@router.get("/websockets/connections", response=Dict[str, Any])
def get_all_websocket_connections(request) -> Dict[str, Any]:
    """
    Get all active WebSocket connections.
    
    Returns:
        Dictionary with list of all active connections:
        - connections: List of connection dictionaries
        - total: Total number of active connections
        - timestamp: Current timestamp
    """
    try:
        metrics = get_websocket_metrics()
        if metrics:
            connections = metrics.get_all_connections()
            return {
                'connections': connections,
                'total': len(connections),
                'timestamp': None
            }
        return {
            'connections': [],
            'total': 0,
            'timestamp': None,
            'error': 'Metrics service unavailable'
        }
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        return {
            'connections': [],
            'total': 0,
            'timestamp': None,
            'error': str(e)
        }


@router.get("/websockets/connections/{user_id}", response=Dict[str, Any])
def get_user_websocket_connections(request, user_id: str) -> Dict[str, Any]:
    """
    Get WebSocket connections for a specific user.
    
    Args:
        user_id: User identifier
        
    Returns:
        Dictionary with user's connection details:
        - user_id: The requested user ID
        - connections: List of user's active connections
        - subscriptions: List of user's active subscriptions
        - timestamp: Current timestamp
    """
    try:
        metrics = get_websocket_metrics()
        if metrics:
            return metrics.get_connection_info(user_id)
        return {
            'user_id': user_id,
            'connections': [],
            'subscriptions': [],
            'timestamp': None,
            'error': 'Metrics service unavailable'
        }
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        return {
            'user_id': user_id,
            'connections': [],
            'subscriptions': [],
            'timestamp': None,
            'error': str(e)
        }


@router.get("/websockets/cleanup", response=Dict[str, Any])
def cleanup_old_websocket_records(request, hours: int = 24) -> Dict[str, Any]:
    """
    Clean up old WebSocket connection records.
    
    Args:
        hours: Number of hours to keep records (default: 24)
        
    Returns:
        Dictionary with cleanup result:
        - message: Status message
        - hours_ago: Records older than this were cleaned up
        - timestamp: Current timestamp
    """
    try:
        metrics = get_websocket_metrics()
        if metrics:
            metrics.cleanup_old_records(hours=hours)
            return {
                'message': f'Cleaned up connection records older than {hours} hours',
                'hours_ago': hours,
                'timestamp': None,
                'status': 'success'
            }
        return {
            'message': 'Metrics service unavailable',
            'hours_ago': hours,
            'timestamp': None,
            'status': 'error'
        }
    except (ValueError, KeyError, TypeError, NetworkError, TimeoutException) as e:
        return {
            'message': f'Cleanup failed: {str(e)}',
            'hours_ago': hours,
            'timestamp': None,
            'status': 'error'
        }
