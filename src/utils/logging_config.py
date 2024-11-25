"""Logging configuration module."""
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from src.config.environment import env

class LoggerConfig:
    """Logger configuration class."""
    
    def __init__(self):
        """Initialize logger configuration."""
        self.log_dir = env.get_path('LOG_DIR')
        self.config = env.get_config('LOGGING')
        self.loggers: Dict[str, logging.Logger] = {}
    
    def get_logger(
        self,
        name: str,
        log_file: Optional[str] = None,
        level: Optional[str] = None
    ) -> logging.Logger:
        """Get or create a logger with the specified configuration."""
        if name in self.loggers:
            return self.loggers[name]
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(level or self.config['LOG_LEVEL'])
        
        # Remove existing handlers
        logger.handlers = []
        
        # Add handlers
        handlers = self._create_handlers(name, log_file)
        for handler in handlers:
            logger.addHandler(handler)
        
        # Store logger
        self.loggers[name] = logger
        return logger
    
    def _create_handlers(
        self,
        name: str,
        log_file: Optional[str] = None
    ) -> list:
        """Create log handlers."""
        handlers = []
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self._create_formatter())
        handlers.append(console_handler)
        
        # File handler
        if log_file:
            file_path = self.log_dir / log_file
        else:
            current_date = datetime.now().strftime('%Y%m%d')
            file_path = self.log_dir / f"{name}_{current_date}.log"
        
        file_handler = logging.handlers.RotatingFileHandler(
            filename=file_path,
            maxBytes=self.config['MAX_BYTES'],
            backupCount=self.config['BACKUP_COUNT']
        )
        file_handler.setFormatter(self._create_formatter())
        handlers.append(file_handler)
        
        return handlers
    
    def _create_formatter(self) -> logging.Formatter:
        """Create log formatter."""
        return logging.Formatter(
            fmt=self.config['FORMAT'],
            datefmt=self.config['DATE_FORMAT']
        )

class Logger:
    """Logger class with context-specific logging methods."""
    
    def __init__(self, name: str, log_file: Optional[str] = None):
        """Initialize logger."""
        self.logger = logger_config.get_logger(name, log_file)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log info message."""
        self.logger.info(message, extra=extra or {})
    
    def error(
        self,
        message: str,
        exc_info: bool = True,
        extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log error message."""
        self.logger.error(message, exc_info=exc_info, extra=extra or {})
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log warning message."""
        self.logger.warning(message, extra=extra or {})
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log debug message."""
        self.logger.debug(message, extra=extra or {})
    
    def critical(
        self,
        message: str,
        exc_info: bool = True,
        extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log critical message."""
        self.logger.critical(message, exc_info=exc_info, extra=extra or {})

class PropertyLogger(Logger):
    """Logger for property-related operations."""
    
    def __init__(self):
        """Initialize property logger."""
        super().__init__('property', 'property.log')
    
    def log_search(self, criteria: Dict[str, Any], results_count: int) -> None:
        """Log property search."""
        self.info(
            f"Property search completed",
            {
                'criteria': criteria,
                'results_count': results_count,
                'operation': 'search'
            }
        )
    
    def log_analysis(
        self,
        property_id: str,
        metrics: Dict[str, float],
        assumptions: Dict[str, Any]
    ) -> None:
        """Log property analysis."""
        self.info(
            f"Property analysis completed for {property_id}",
            {
                'property_id': property_id,
                'metrics': metrics,
                'assumptions': assumptions,
                'operation': 'analysis'
            }
        )
    
    def log_api_error(
        self,
        operation: str,
        error: Exception,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log API error."""
        self.error(
            f"API error during {operation}",
            extra={
                'operation': operation,
                'error_type': type(error).__name__,
                'error_message': str(error),
                'details': details or {}
            }
        )

class InvestmentLogger(Logger):
    """Logger for investment-related operations."""
    
    def __init__(self):
        """Initialize investment logger."""
        super().__init__('investment', 'investment.log')
    
    def log_calculation(
        self,
        calculation_type: str,
        inputs: Dict[str, Any],
        results: Dict[str, Any]
    ) -> None:
        """Log investment calculation."""
        self.info(
            f"{calculation_type} calculation completed",
            {
                'calculation_type': calculation_type,
                'inputs': inputs,
                'results': results,
                'operation': 'calculation'
            }
        )
    
    def log_assumption_change(
        self,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any]
    ) -> None:
        """Log investment assumption changes."""
        self.info(
            "Investment assumptions updated",
            {
                'old_values': old_values,
                'new_values': new_values,
                'operation': 'assumption_update'
            }
        )

class UserLogger(Logger):
    """Logger for user-related operations."""
    
    def __init__(self):
        """Initialize user logger."""
        super().__init__('user', 'user.log')
    
    def log_session_start(self, session_id: str) -> None:
        """Log session start."""
        self.info(
            "User session started",
            {
                'session_id': session_id,
                'operation': 'session_start'
            }
        )
    
    def log_session_end(self, session_id: str, duration: float) -> None:
        """Log session end."""
        self.info(
            "User session ended",
            {
                'session_id': session_id,
                'duration': duration,
                'operation': 'session_end'
            }
        )
    
    def log_action(
        self,
        session_id: str,
        action: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log user action."""
        self.info(
            f"User action: {action}",
            {
                'session_id': session_id,
                'action': action,
                'details': details or {},
                'operation': 'user_action'
            }
        )

# Create singleton instances
logger_config = LoggerConfig()
property_logger = PropertyLogger()
investment_logger = InvestmentLogger()
user_logger = UserLogger()
