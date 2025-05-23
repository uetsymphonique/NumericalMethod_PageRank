import logging
from typing import Optional

def setup_logging(log_level: str = 'INFO') -> None:
    """Configure logging with the specified level"""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger for the specified module"""
    return logging.getLogger(name) 