"""Logging configuration."""
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from .settings import DATA_DIR

# Create logs directory
LOGS_DIR = DATA_DIR / 'logs'
if not LOGS_DIR.exists():
    LOGS_DIR.mkdir(parents=True)

def setup_logging(name: str = __name__) -> logging.Logger:
    """Configure and return a logger instance."""
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # File handler (rotating)
    log_file = LOGS_DIR / f"{datetime.now().strftime('%Y%m')}_app.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create default logger
logger = setup_logging('real_estate_analyzer')

def log_api_request(endpoint: str, params: dict) -> None:
    """Log API request details."""
    logger.info(f"API Request - Endpoint: {endpoint}, Params: {params}")

def log_api_error(endpoint: str, error: str) -> None:
    """Log API error details."""
    logger.error(f"API Error - Endpoint: {endpoint}, Error: {error}")

def log_calculation_error(calc_type: str, error: str) -> None:
    """Log calculation error details."""
    logger.error(f"Calculation Error - Type: {calc_type}, Error: {error}")

def log_validation_error(data_type: str, errors: dict) -> None:
    """Log validation error details."""
    logger.warning(f"Validation Error - Type: {data_type}, Errors: {errors}")

def log_cache_operation(operation: str, key: str) -> None:
    """Log cache operation details."""
    logger.debug(f"Cache {operation} - Key: {key}")

def log_user_action(action: str, details: dict) -> None:
    """Log user action details."""
    logger.info(f"User Action - {action}: {details}")
