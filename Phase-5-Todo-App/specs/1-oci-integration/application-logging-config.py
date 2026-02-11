"""
Structured logging configuration for application services
This configuration ensures all services output structured JSON logs for centralized logging
"""

import logging
import json
import sys
from datetime import datetime
from pythonjsonlogger import jsonlogger
import traceback
from typing import Dict, Any, Optional


class StructuredLogger:
    """
    Configures structured JSON logging for application services
    """

    def __init__(self, service_name: str, log_level: str = "INFO"):
        self.service_name = service_name
        self.log_level = getattr(logging, log_level.upper())
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup structured JSON logger"""
        logger = logging.getLogger(self.service_name)
        logger.setLevel(self.log_level)

        # Prevent duplicate handlers
        if logger.handlers:
            logger.handlers.clear()

        # Create JSON formatter
        json_formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s",
            rename_fields={
                'asctime': '@timestamp',
                'levelname': 'level',
                'name': 'service',
                'message': 'message'
            },
            static_fields={
                'service': self.service_name,
                'environment': 'production',
                'version': '1.0.0'
            }
        )

        # Console handler for Kubernetes
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(json_formatter)
        logger.addHandler(console_handler)

        return logger

    def log_request(self, method: str, path: str, status_code: int, duration_ms: float,
                   user_id: Optional[str] = None, correlation_id: Optional[str] = None):
        """Log HTTP request details"""
        extra = {
            'event': 'request',
            'method': method,
            'path': path,
            'status': status_code,
            'duration_ms': duration_ms
        }

        if user_id:
            extra['user_id'] = user_id
        if correlation_id:
            extra['correlation_id'] = correlation_id

        self.logger.info("Request completed", extra=extra)

    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None,
                  correlation_id: Optional[str] = None):
        """Log error with full context"""
        extra = {
            'event': 'error',
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc()
        }

        if context:
            extra.update(context)
        if correlation_id:
            extra['correlation_id'] = correlation_id

        self.logger.error("Error occurred", extra=extra)

    def log_event(self, event_type: str, data: Dict[str, Any],
                  correlation_id: Optional[str] = None, user_id: Optional[str] = None):
        """Log business events"""
        extra = {
            'event': event_type,
            'data': data
        }

        if correlation_id:
            extra['correlation_id'] = correlation_id
        if user_id:
            extra['user_id'] = user_id

        self.logger.info(f"Event: {event_type}", extra=extra)

    def log_metric(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Log application metrics"""
        extra = {
            'event': 'metric',
            'metric_name': metric_name,
            'value': value
        }

        if tags:
            extra.update(tags)

        self.logger.info(f"Metric: {metric_name}", extra=extra)


# Example usage for different services
def configure_backend_logging():
    """Configure logging for backend service"""
    return StructuredLogger("todo-backend")


def configure_frontend_logging():
    """Configure logging for frontend service"""
    return StructuredLogger("todo-frontend")


def configure_notification_logging():
    """Configure logging for notification service"""
    return StructuredLogger("notification-service")


def configure_scheduler_logging():
    """Configure logging for scheduler service"""
    return StructuredLogger("scheduler-service")


# Correlation ID utility
class CorrelationIdManager:
    """Manages correlation IDs for distributed tracing"""

    def __init__(self):
        self._current_correlation_id = None

    def set_correlation_id(self, correlation_id: Optional[str] = None):
        """Set correlation ID for current context"""
        if correlation_id:
            self._current_correlation_id = correlation_id
        else:
            import uuid
            self._current_correlation_id = str(uuid.uuid4())

    def get_correlation_id(self) -> Optional[str]:
        """Get current correlation ID"""
        return self._current_correlation_id

    def clear_correlation_id(self):
        """Clear current correlation ID"""
        self._current_correlation_id = None


# Middleware for Flask/FastAPI to handle correlation IDs
def correlation_id_middleware(request, logger: StructuredLogger):
    """Middleware to extract or generate correlation ID from request"""
    correlation_id = request.headers.get('X-Correlation-ID') or request.headers.get('X-Request-ID')

    if not correlation_id:
        import uuid
        correlation_id = str(uuid.uuid4())

    # Add correlation ID to request context
    request.correlation_id = correlation_id

    # Log request start
    logger.logger.info("Request started", extra={'correlation_id': correlation_id})

    return correlation_id


# Example usage in a service
if __name__ == "__main__":
    # Configure logger for a service
    logger = StructuredLogger("todo-backend", "INFO")

    # Example of different log types
    logger.log_request("GET", "/api/tasks", 200, 150.5, user_id="user123", correlation_id="corr123")

    logger.log_event("task.created", {"task_id": "task456", "user_id": "user123"},
                     correlation_id="corr123", user_id="user123")

    try:
        # Simulate an error
        raise ValueError("Something went wrong")
    except Exception as e:
        logger.log_error(e, context={"component": "task_service"}, correlation_id="corr123")

    logger.log_metric("response_time", 150.5, tags={"endpoint": "/api/tasks", "method": "GET"})

    print("Structured logging configuration examples created successfully!")