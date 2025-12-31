"""
Structured logging configuration with JSON format and correlation IDs.
"""
import logging
import uuid
from pythonjsonlogger import jsonlogger


class CorrelationIDFilter(logging.Filter):
    """Add correlation ID to log records."""
    
    def filter(self, record):
        if not hasattr(record, 'correlation_id'):
            record.correlation_id = str(uuid.uuid4())
        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields."""
    
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add timestamp
        if not log_record.get('timestamp'):
            log_record['timestamp'] = record.created
        
        # Add level name
        if log_record.get('level'):
            log_record['level'] = record.levelname
        else:
            log_record['level'] = record.levelname
        
        # Add logger name
        log_record['logger'] = record.name
        
        # Add correlation ID if present
        if hasattr(record, 'correlation_id'):
            log_record['correlation_id'] = record.correlation_id
        
        # Add tenant info if present
        if hasattr(record, 'tenant_id'):
            log_record['tenant_id'] = record.tenant_id
        
        # Add user info if present
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id


def get_logging_config(debug=False):
    """
    Get logging configuration dictionary.
    
    Args:
        debug: If True, use console logging. If False, use JSON logging.
    
    Returns:
        dict: Logging configuration
    """
    if debug:
        # Development: Human-readable console logging
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'filters': {
                'correlation_id': {
                    '()': 'possystem.logging_config.CorrelationIDFilter',
                },
            },
            'formatters': {
                'verbose': {
                    'format': '[{levelname}] {asctime} {name} {correlation_id} - {message}',
                    'style': '{',
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'filters': ['correlation_id'],
                    'formatter': 'verbose',
                },
            },
            'root': {
                'handlers': ['console'],
                'level': 'INFO',
            },
            'loggers': {
                'django': {
                    'handlers': ['console'],
                    'level': 'INFO',
                    'propagate': False,
                },
                'django.db.backends': {
                    'handlers': ['console'],
                    'level': 'WARNING',  # Only show SQL warnings/errors
                    'propagate': False,
                },
            },
        }
    else:
        # Production: JSON logging
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'filters': {
                'correlation_id': {
                    '()': 'possystem.logging_config.CorrelationIDFilter',
                },
            },
            'formatters': {
                'json': {
                    '()': 'possystem.logging_config.CustomJsonFormatter',
                    'format': '%(timestamp)s %(level)s %(name)s %(message)s',
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'filters': ['correlation_id'],
                    'formatter': 'json',
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': 'logs/app.log',
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 10,
                    'filters': ['correlation_id'],
                    'formatter': 'json',
                },
            },
            'root': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
            },
            'loggers': {
                'django': {
                    'handlers': ['console', 'file'],
                    'level': 'INFO',
                    'propagate': False,
                },
                'django.db.backends': {
                    'handlers': ['console', 'file'],
                    'level': 'WARNING',
                    'propagate': False,
                },
            },
        }
