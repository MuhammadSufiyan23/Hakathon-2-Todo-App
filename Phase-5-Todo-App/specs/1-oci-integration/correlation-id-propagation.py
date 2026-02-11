"""
Correlation ID propagation across services
This module implements correlation ID propagation for distributed tracing
"""

import uuid
from typing import Optional, Dict, Any
from contextlib import contextmanager
import threading
from functools import wraps


class CorrelationIdContext:
    """
    Thread-local storage for correlation ID context
    """
    _local = threading.local()

    @classmethod
    def set_correlation_id(cls, correlation_id: str):
        """Set correlation ID in thread-local context"""
        cls._local.correlation_id = correlation_id

    @classmethod
    def get_correlation_id(cls) -> Optional[str]:
        """Get correlation ID from thread-local context"""
        return getattr(cls._local, 'correlation_id', None)

    @classmethod
    def clear_correlation_id(cls):
        """Clear correlation ID from thread-local context"""
        if hasattr(cls._local, 'correlation_id'):
            delattr(cls._local, 'correlation_id')


@contextmanager
def correlation_id_context(correlation_id: Optional[str] = None):
    """
    Context manager for correlation ID
    """
    original_id = CorrelationIdContext.get_correlation_id()

    if correlation_id is None:
        correlation_id = str(uuid.uuid4())

    CorrelationIdContext.set_correlation_id(correlation_id)

    try:
        yield correlation_id
    finally:
        # Restore original correlation ID
        if original_id is not None:
            CorrelationIdContext.set_correlation_id(original_id)
        else:
            CorrelationIdContext.clear_correlation_id()


def with_correlation_id(func):
    """
    Decorator to ensure correlation ID is propagated through function calls
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        correlation_id = CorrelationIdContext.get_correlation_id()

        if correlation_id is None:
            correlation_id = str(uuid.uuid4())
            CorrelationIdContext.set_correlation_id(correlation_id)

        # Add correlation ID to kwargs if not already present
        if 'correlation_id' not in kwargs:
            kwargs['correlation_id'] = correlation_id

        return func(*args, **kwargs)

    return wrapper


def get_or_create_correlation_id(headers: Optional[Dict[str, str]] = None) -> str:
    """
    Extract correlation ID from headers or create a new one

    Args:
        headers: Dictionary of request headers

    Returns:
        Correlation ID string
    """
    if headers:
        # Try different common header names for correlation IDs
        correlation_id = (
            headers.get('X-Correlation-ID') or
            headers.get('X-Request-ID') or
            headers.get('X-Trace-ID') or
            headers.get('Traceparent')  # W3C Trace Context
        )

        if correlation_id:
            return correlation_id

    # Generate new correlation ID if none found
    return str(uuid.uuid4())


def inject_correlation_id_headers(headers: Dict[str, str], correlation_id: str) -> Dict[str, str]:
    """
    Inject correlation ID into headers for outbound requests

    Args:
        headers: Existing headers dictionary
        correlation_id: Correlation ID to inject

    Returns:
        Updated headers dictionary
    """
    updated_headers = headers.copy()
    updated_headers['X-Correlation-ID'] = correlation_id
    updated_headers['X-Request-ID'] = correlation_id
    return updated_headers


# Dapr-specific correlation ID handling
class DaprCorrelationIdHandler:
    """
    Handler for correlation ID propagation through Dapr service invocation
    """

    @staticmethod
    def prepare_dapr_invocation_metadata(correlation_id: str) -> Dict[str, Any]:
        """
        Prepare metadata for Dapr service invocation with correlation ID
        """
        return {
            'headers': {
                'X-Correlation-ID': correlation_id,
                'X-Request-ID': correlation_id
            }
        }

    @staticmethod
    def extract_from_dapr_metadata(metadata: Optional[Dict[str, Any]]) -> Optional[str]:
        """
        Extract correlation ID from Dapr invocation metadata
        """
        if not metadata:
            return None

        headers = metadata.get('headers', {})
        return (
            headers.get('X-Correlation-ID') or
            headers.get('X-Request-ID') or
            headers.get('X-Trace-ID')
        )


# FastAPI/Starlette middleware for correlation ID
def correlation_id_middleware(app):
    """
    ASGI middleware for correlation ID propagation in FastAPI applications
    """
    async def middleware(scope, receive, send):
        if scope['type'] != 'http':
            await app(scope, receive, send)
            return

        # Extract correlation ID from headers
        headers = {}
        for name, value in scope['headers']:
            headers[name.decode()] = value.decode()

        correlation_id = get_or_create_correlation_id(headers)
        CorrelationIdContext.set_correlation_id(correlation_id)

        # Add correlation ID to response headers
        async def custom_send(message):
            if message['type'] == 'http.response.start':
                headers = message.get('headers', [])
                headers.append([b'x-correlation-id', correlation_id.encode()])
                message['headers'] = headers
            await send(message)

        await app(scope, receive, custom_send)

    return middleware


# Flask middleware for correlation ID
class FlaskCorrelationIdMiddleware:
    """
    WSGI middleware for correlation ID propagation in Flask applications
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Extract correlation ID from headers
        headers = {}
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                header_name = key[5:].replace('_', '-').lower()
                headers[header_name] = value

        correlation_id = get_or_create_correlation_id(headers)
        CorrelationIdContext.set_correlation_id(correlation_id)

        def custom_start_response(status, headers, exc_info=None):
            headers.append(('X-Correlation-ID', correlation_id))
            return start_response(status, headers, exc_info)

        return self.app(environ, custom_start_response)


# Example usage in different services
class ServiceCorrelationManager:
    """
    Manager for correlation ID handling in different services
    """

    def __init__(self, service_name: str):
        self.service_name = service_name

    def process_request(self, request_headers: Dict[str, str]):
        """
        Process incoming request and establish correlation context
        """
        correlation_id = get_or_create_correlation_id(request_headers)
        CorrelationIdContext.set_correlation_id(correlation_id)

        return correlation_id

    def make_service_call(self, target_service: str, data: Dict[str, Any],
                         headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Make a service call with correlation ID propagation
        """
        correlation_id = CorrelationIdContext.get_correlation_id()

        if not correlation_id:
            correlation_id = str(uuid.uuid4())
            CorrelationIdContext.set_correlation_id(correlation_id)

        if headers is None:
            headers = {}

        # Inject correlation ID into headers
        headers = inject_correlation_id_headers(headers, correlation_id)

        # Simulate service call (in real implementation, this would make actual HTTP/Dapr call)
        print(f"[{self.service_name}] Calling {target_service} with correlation ID: {correlation_id}")

        # Return mock response with headers
        return {
            'status': 'success',
            'correlation_id': correlation_id,
            'headers': headers
        }

    def log_with_correlation(self, message: str, level: str = 'INFO', **kwargs):
        """
        Log message with current correlation ID
        """
        correlation_id = CorrelationIdContext.get_correlation_id()

        log_entry = {
            'service': self.service_name,
            'level': level,
            'message': message,
            'timestamp': str(uuid.uuid4()),  # In real implementation, use actual timestamp
            **kwargs
        }

        if correlation_id:
            log_entry['correlation_id'] = correlation_id

        print(f"LOG: {log_entry}")


# Example usage
if __name__ == "__main__":
    # Example: Backend service making a call to notification service
    backend_manager = ServiceCorrelationManager("todo-backend")

    # Simulate incoming request with correlation ID
    incoming_headers = {'X-Correlation-ID': 'abc-123-def-456'}
    correlation_id = backend_manager.process_request(incoming_headers)

    print(f"Processing request with correlation ID: {correlation_id}")

    # Make a call to notification service, correlation ID will be propagated
    response = backend_manager.make_service_call(
        target_service="notification-service",
        data={"task_id": "task123", "user_id": "user456", "action": "reminder_sent"}
    )

    # Log with correlation ID
    backend_manager.log_with_correlation(
        "Task processed successfully",
        task_id="task123",
        user_id="user456"
    )

    print("\nCorrelation ID propagation example completed!")

    # Example using context manager
    print("\nUsing correlation ID context manager:")
    with correlation_id_context() as cid:
        print(f"Generated correlation ID: {cid}")

        backend_manager.log_with_correlation("Action performed in context")

        # Simulate calling another function that should inherit the correlation ID
        @with_correlation_id
        def some_business_logic(data, correlation_id=None):
            print(f"Business logic running with correlation ID: {correlation_id}")
            return {"result": "success", "correlation_id": correlation_id}

        result = some_business_logic({"action": "create_task"})
        print(f"Result: {result}")