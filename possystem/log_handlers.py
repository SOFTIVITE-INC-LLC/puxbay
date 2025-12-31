import logging
import traceback

class DatabaseLogHandler(logging.Handler):
    """
    Log handler that writes logs to the database using the SystemLog model.
    """
    def emit(self, record):
        from accounts.models import SystemLog  # Late import to avoid registry errors
        
        try:
            # Format exception/traceback if present
            trace = None
            if record.exc_info:
                trace = traceback.format_exc()
            
            log_entry = SystemLog(
                level=record.levelname,
                module=record.module,
                message=record.getMessage(),
                traceback=trace,
                path=record.pathname
            )
            log_entry.save()
            
        except Exception:
            # Ensure we don't start an infinite loop if DB logging fails
            # Fallback to standard error output or ignore
            pass
