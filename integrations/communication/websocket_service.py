"""
WebSocket Real-time Communication Service
Handles real-time notifications and communication for FinClick.AI platform
"""

import asyncio
import websockets
import json
import logging
import time
import jwt
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from functools import wraps
import uuid
import redis.asyncio as redis

# Configure logging
logger = logging.getLogger(__name__)

class MessageType(Enum):
    NOTIFICATION = "notification"
    ALERT = "alert"
    PRICE_UPDATE = "price_update"
    PORTFOLIO_UPDATE = "portfolio_update"
    TRADE_CONFIRMATION = "trade_confirmation"
    MARKET_NEWS = "market_news"
    SYSTEM_MESSAGE = "system_message"
    USER_MESSAGE = "user_message"
    PING = "ping"
    PONG = "pong"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    ERROR = "error"

class NotificationPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class SubscriptionType(Enum):
    STOCK_PRICES = "stock_prices"
    PORTFOLIO = "portfolio"
    ALERTS = "alerts"
    MARKET_NEWS = "market_news"
    SYSTEM_NOTIFICATIONS = "system_notifications"

@dataclass
class WebSocketMessage:
    type: MessageType
    data: Dict[str, Any]
    timestamp: datetime = None
    message_id: str = None
    priority: NotificationPriority = NotificationPriority.NORMAL
    expires_at: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.message_id is None:
            self.message_id = str(uuid.uuid4())

@dataclass
class ClientConnection:
    websocket: websockets.WebSocketServerProtocol
    user_id: str
    connection_id: str
    subscriptions: Set[str]
    last_ping: datetime
    authenticated: bool = False
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.subscriptions is None:
            self.subscriptions = set()
        if self.metadata is None:
            self.metadata = {}

class WebSocketService:
    """Comprehensive WebSocket service for real-time communication - FinClick.AI"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8765,
        jwt_secret: str = None,
        redis_url: str = None,
        ping_interval: int = 30,
        ping_timeout: int = 10,
        max_connections_per_user: int = 5
    ):
        self.host = host
        self.port = port
        self.jwt_secret = jwt_secret
        self.redis_url = redis_url
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        self.max_connections_per_user = max_connections_per_user

        # Connection management
        self.connections: Dict[str, ClientConnection] = {}
        self.user_connections: Dict[str, Set[str]] = {}
        self.subscription_connections: Dict[str, Set[str]] = {}

        # Redis for scaling across multiple instances
        self.redis_client = None
        if redis_url:
            self.redis_client = redis.from_url(redis_url)

        # Message handlers
        self.message_handlers: Dict[MessageType, Callable] = {
            MessageType.PING: self._handle_ping,
            MessageType.SUBSCRIBE: self._handle_subscribe,
            MessageType.UNSUBSCRIBE: self._handle_unsubscribe,
        }

        # Server instance
        self.server = None
        self.running = False

        logger.info(f"WebSocket service initialized on {host}:{port}")

    async def start_server(self):
        """Start WebSocket server"""
        try:
            self.server = await websockets.serve(
                self._handle_client,
                self.host,
                self.port,
                ping_interval=self.ping_interval,
                ping_timeout=self.ping_timeout
            )
            self.running = True

            # Start background tasks
            asyncio.create_task(self._cleanup_connections())
            asyncio.create_task(self._redis_subscriber())

            logger.info(f"WebSocket server started on {self.host}:{self.port}")

        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {str(e)}")
            raise

    async def stop_server(self):
        """Stop WebSocket server"""
        try:
            self.running = False

            if self.server:
                self.server.close()
                await self.server.wait_closed()

            # Close all connections
            for connection in list(self.connections.values()):
                await connection.websocket.close()

            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()

            logger.info("WebSocket server stopped")

        except Exception as e:
            logger.error(f"Error stopping WebSocket server: {str(e)}")

    async def _handle_client(self, websocket, path):
        """Handle new client connection"""
        connection_id = str(uuid.uuid4())
        client_connection = None

        try:
            # Extract user authentication from path or query params
            user_id = await self._authenticate_connection(websocket, path)

            if not user_id:
                await websocket.close(code=4001, reason="Authentication required")
                return

            # Check connection limits
            if not await self._check_connection_limits(user_id):
                await websocket.close(code=4002, reason="Connection limit exceeded")
                return

            # Create client connection
            client_connection = ClientConnection(
                websocket=websocket,
                user_id=user_id,
                connection_id=connection_id,
                subscriptions=set(),
                last_ping=datetime.now(),
                authenticated=True
            )

            # Register connection
            await self._register_connection(client_connection)

            logger.info(f"Client connected: {user_id} ({connection_id})")

            # Handle messages
            async for message in websocket:
                await self._process_message(client_connection, message)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {connection_id}")
        except Exception as e:
            logger.error(f"Error handling client {connection_id}: {str(e)}")
        finally:
            if client_connection:
                await self._unregister_connection(client_connection)

    async def _authenticate_connection(self, websocket, path) -> Optional[str]:
        """Authenticate WebSocket connection"""
        try:
            # Extract token from query parameters or headers
            token = None

            # Try to get token from query params
            if '?' in path:
                query_params = path.split('?')[1]
                for param in query_params.split('&'):
                    if param.startswith('token='):
                        token = param.split('=')[1]
                        break

            # Try to get token from headers
            if not token:
                auth_header = websocket.request_headers.get('Authorization')
                if auth_header and auth_header.startswith('Bearer '):
                    token = auth_header[7:]

            if not token:
                return None

            # Verify JWT token
            if self.jwt_secret:
                try:
                    payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
                    user_id = payload.get('user_id')

                    # Check token expiration
                    exp = payload.get('exp')
                    if exp and datetime.fromtimestamp(exp) < datetime.now():
                        return None

                    return user_id
                except jwt.InvalidTokenError:
                    return None
            else:
                # For development - extract user_id directly from token
                try:
                    payload = jwt.decode(token, options={"verify_signature": False})
                    return payload.get('user_id')
                except:
                    return None

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None

    async def _check_connection_limits(self, user_id: str) -> bool:
        """Check if user has exceeded connection limits"""
        user_connection_count = len(self.user_connections.get(user_id, set()))
        return user_connection_count < self.max_connections_per_user

    async def _register_connection(self, connection: ClientConnection):
        """Register new connection"""
        # Add to connections
        self.connections[connection.connection_id] = connection

        # Add to user connections
        if connection.user_id not in self.user_connections:
            self.user_connections[connection.user_id] = set()
        self.user_connections[connection.user_id].add(connection.connection_id)

        # Notify Redis about new connection
        if self.redis_client:
            await self.redis_client.publish(
                'websocket_events',
                json.dumps({
                    'type': 'connection_opened',
                    'user_id': connection.user_id,
                    'connection_id': connection.connection_id
                })
            )

    async def _unregister_connection(self, connection: ClientConnection):
        """Unregister connection"""
        # Remove from connections
        if connection.connection_id in self.connections:
            del self.connections[connection.connection_id]

        # Remove from user connections
        if connection.user_id in self.user_connections:
            self.user_connections[connection.user_id].discard(connection.connection_id)
            if not self.user_connections[connection.user_id]:
                del self.user_connections[connection.user_id]

        # Remove from subscription connections
        for subscription in connection.subscriptions:
            if subscription in self.subscription_connections:
                self.subscription_connections[subscription].discard(connection.connection_id)
                if not self.subscription_connections[subscription]:
                    del self.subscription_connections[subscription]

        # Notify Redis about connection closure
        if self.redis_client:
            await self.redis_client.publish(
                'websocket_events',
                json.dumps({
                    'type': 'connection_closed',
                    'user_id': connection.user_id,
                    'connection_id': connection.connection_id
                })
            )

    async def _process_message(self, connection: ClientConnection, message: str):
        """Process incoming message from client"""
        try:
            data = json.loads(message)
            message_type = MessageType(data.get('type'))

            # Update last activity
            connection.last_ping = datetime.now()

            # Handle message
            if message_type in self.message_handlers:
                await self.message_handlers[message_type](connection, data)
            else:
                logger.warning(f"Unhandled message type: {message_type}")
                await self._send_error(connection, f"Unhandled message type: {message_type}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from {connection.connection_id}")
            await self._send_error(connection, "Invalid JSON format")
        except ValueError:
            logger.error(f"Invalid message type from {connection.connection_id}")
            await self._send_error(connection, "Invalid message type")
        except Exception as e:
            logger.error(f"Error processing message from {connection.connection_id}: {str(e)}")
            await self._send_error(connection, "Internal server error")

    async def _handle_ping(self, connection: ClientConnection, data: Dict):
        """Handle ping message"""
        await self._send_message(connection, WebSocketMessage(
            type=MessageType.PONG,
            data={'timestamp': datetime.now().isoformat()}
        ))

    async def _handle_subscribe(self, connection: ClientConnection, data: Dict):
        """Handle subscription request"""
        try:
            subscription = data.get('subscription')
            if not subscription:
                await self._send_error(connection, "Subscription type required")
                return

            # Add subscription
            connection.subscriptions.add(subscription)

            # Add to subscription connections
            if subscription not in self.subscription_connections:
                self.subscription_connections[subscription] = set()
            self.subscription_connections[subscription].add(connection.connection_id)

            logger.info(f"Client {connection.connection_id} subscribed to {subscription}")

            # Send confirmation
            await self._send_message(connection, WebSocketMessage(
                type=MessageType.NOTIFICATION,
                data={
                    'message': f'Subscribed to {subscription}',
                    'subscription': subscription
                }
            ))

        except Exception as e:
            logger.error(f"Error handling subscription: {str(e)}")
            await self._send_error(connection, "Failed to process subscription")

    async def _handle_unsubscribe(self, connection: ClientConnection, data: Dict):
        """Handle unsubscription request"""
        try:
            subscription = data.get('subscription')
            if not subscription:
                await self._send_error(connection, "Subscription type required")
                return

            # Remove subscription
            connection.subscriptions.discard(subscription)

            # Remove from subscription connections
            if subscription in self.subscription_connections:
                self.subscription_connections[subscription].discard(connection.connection_id)
                if not self.subscription_connections[subscription]:
                    del self.subscription_connections[subscription]

            logger.info(f"Client {connection.connection_id} unsubscribed from {subscription}")

            # Send confirmation
            await self._send_message(connection, WebSocketMessage(
                type=MessageType.NOTIFICATION,
                data={
                    'message': f'Unsubscribed from {subscription}',
                    'subscription': subscription
                }
            ))

        except Exception as e:
            logger.error(f"Error handling unsubscription: {str(e)}")
            await self._send_error(connection, "Failed to process unsubscription")

    async def _send_message(self, connection: ClientConnection, message: WebSocketMessage):
        """Send message to specific connection"""
        try:
            if connection.websocket.closed:
                return

            message_data = {
                'type': message.type.value,
                'data': message.data,
                'timestamp': message.timestamp.isoformat(),
                'message_id': message.message_id,
                'priority': message.priority.value
            }

            if message.expires_at:
                message_data['expires_at'] = message.expires_at.isoformat()

            await connection.websocket.send(json.dumps(message_data))

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed: {connection.connection_id}")
        except Exception as e:
            logger.error(f"Error sending message to {connection.connection_id}: {str(e)}")

    async def _send_error(self, connection: ClientConnection, error_message: str):
        """Send error message to connection"""
        await self._send_message(connection, WebSocketMessage(
            type=MessageType.ERROR,
            data={'error': error_message}
        ))

    async def send_to_user(self, user_id: str, message: WebSocketMessage):
        """Send message to all connections of a specific user"""
        if user_id not in self.user_connections:
            return

        connection_ids = list(self.user_connections[user_id])
        for connection_id in connection_ids:
            if connection_id in self.connections:
                await self._send_message(self.connections[connection_id], message)

    async def send_to_subscription(self, subscription: str, message: WebSocketMessage):
        """Send message to all connections subscribed to a topic"""
        if subscription not in self.subscription_connections:
            return

        connection_ids = list(self.subscription_connections[subscription])
        for connection_id in connection_ids:
            if connection_id in self.connections:
                await self._send_message(self.connections[connection_id], message)

    async def broadcast_to_all(self, message: WebSocketMessage, exclude_user: str = None):
        """Broadcast message to all connected users"""
        for connection in list(self.connections.values()):
            if exclude_user and connection.user_id == exclude_user:
                continue
            await self._send_message(connection, message)

    async def send_notification(
        self,
        user_id: str,
        title: str,
        content: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        action_url: str = None,
        expires_in_minutes: int = None
    ):
        """Send notification to user"""
        notification_data = {
            'title': title,
            'content': content,
            'action_url': action_url
        }

        expires_at = None
        if expires_in_minutes:
            expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)

        message = WebSocketMessage(
            type=MessageType.NOTIFICATION,
            data=notification_data,
            priority=priority,
            expires_at=expires_at
        )

        await self.send_to_user(user_id, message)

        # Also publish to Redis for other instances
        if self.redis_client:
            await self.redis_client.publish(
                'user_notifications',
                json.dumps({
                    'user_id': user_id,
                    'message': asdict(message)
                })
            )

    async def send_price_update(self, symbol: str, price_data: Dict):
        """Send stock price update to subscribers"""
        message = WebSocketMessage(
            type=MessageType.PRICE_UPDATE,
            data={
                'symbol': symbol,
                **price_data
            }
        )

        await self.send_to_subscription(f"stock_prices:{symbol}", message)
        await self.send_to_subscription("stock_prices:all", message)

    async def send_portfolio_update(self, user_id: str, portfolio_data: Dict):
        """Send portfolio update to user"""
        message = WebSocketMessage(
            type=MessageType.PORTFOLIO_UPDATE,
            data=portfolio_data
        )

        await self.send_to_user(user_id, message)

    async def send_market_news(self, news_data: Dict):
        """Send market news to subscribers"""
        message = WebSocketMessage(
            type=MessageType.MARKET_NEWS,
            data=news_data
        )

        await self.send_to_subscription("market_news", message)

    async def send_system_alert(self, alert_data: Dict, priority: NotificationPriority = NotificationPriority.HIGH):
        """Send system-wide alert"""
        message = WebSocketMessage(
            type=MessageType.ALERT,
            data=alert_data,
            priority=priority
        )

        await self.broadcast_to_all(message)

    async def _cleanup_connections(self):
        """Background task to cleanup stale connections"""
        while self.running:
            try:
                current_time = datetime.now()
                stale_connections = []

                for connection in self.connections.values():
                    # Check if connection is stale (no ping for 2x ping interval)
                    if (current_time - connection.last_ping).total_seconds() > (self.ping_interval * 2):
                        stale_connections.append(connection)

                # Close stale connections
                for connection in stale_connections:
                    try:
                        await connection.websocket.close(code=4003, reason="Connection timeout")
                    except:
                        pass

                await asyncio.sleep(self.ping_interval)

            except Exception as e:
                logger.error(f"Error in cleanup task: {str(e)}")
                await asyncio.sleep(5)

    async def _redis_subscriber(self):
        """Background task to handle Redis pub/sub for scaling"""
        if not self.redis_client:
            return

        try:
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe('user_notifications', 'price_updates', 'system_alerts')

            while self.running:
                try:
                    message = await pubsub.get_message(timeout=1.0)
                    if message and message['type'] == 'message':
                        await self._handle_redis_message(message)

                except Exception as e:
                    logger.error(f"Error processing Redis message: {str(e)}")

        except Exception as e:
            logger.error(f"Error in Redis subscriber: {str(e)}")

    async def _handle_redis_message(self, redis_message: Dict):
        """Handle message from Redis pub/sub"""
        try:
            channel = redis_message['channel'].decode('utf-8')
            data = json.loads(redis_message['data'].decode('utf-8'))

            if channel == 'user_notifications':
                user_id = data['user_id']
                message_data = data['message']
                message = WebSocketMessage(**message_data)
                await self.send_to_user(user_id, message)

            elif channel == 'price_updates':
                symbol = data['symbol']
                price_data = data['price_data']
                await self.send_price_update(symbol, price_data)

            elif channel == 'system_alerts':
                alert_data = data['alert_data']
                priority = NotificationPriority(data.get('priority', 'normal'))
                await self.send_system_alert(alert_data, priority)

        except Exception as e:
            logger.error(f"Error handling Redis message: {str(e)}")

    def get_connection_stats(self) -> Dict:
        """Get connection statistics"""
        return {
            'total_connections': len(self.connections),
            'unique_users': len(self.user_connections),
            'subscriptions': {
                subscription: len(connections)
                for subscription, connections in self.subscription_connections.items()
            },
            'server_running': self.running
        }

# Utility functions
async def create_websocket_service(
    host: str = "localhost",
    port: int = 8765,
    jwt_secret: str = None,
    redis_url: str = None,
    ping_interval: int = 30,
    ping_timeout: int = 10,
    max_connections_per_user: int = 5
) -> WebSocketService:
    """Factory function to create WebSocketService instance"""
    return WebSocketService(
        host, port, jwt_secret, redis_url,
        ping_interval, ping_timeout, max_connections_per_user
    )

def create_jwt_token(user_id: str, secret: str, expires_in_hours: int = 24) -> str:
    """Create JWT token for WebSocket authentication"""
    payload = {
        'user_id': user_id,
        'exp': datetime.now() + timedelta(hours=expires_in_hours),
        'iat': datetime.now()
    }
    return jwt.encode(payload, secret, algorithm='HS256')

def create_notification_message(
    title: str,
    content: str,
    priority: NotificationPriority = NotificationPriority.NORMAL,
    action_url: str = None,
    expires_in_minutes: int = None
) -> WebSocketMessage:
    """Create notification message"""
    notification_data = {
        'title': title,
        'content': content
    }

    if action_url:
        notification_data['action_url'] = action_url

    expires_at = None
    if expires_in_minutes:
        expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)

    return WebSocketMessage(
        type=MessageType.NOTIFICATION,
        data=notification_data,
        priority=priority,
        expires_at=expires_at
    )