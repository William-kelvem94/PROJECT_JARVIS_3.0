"""
JARVIS 4.0 Utilities - Logger
Structured logging with Loguru
"""
import sys
from loguru import logger
from pathlib import Path

from core.config import settings

def setup_logger(name: str = None):
    """Setup structured logging with Loguru"""
    
    # Remove default handler
    logger.remove()
    
    # Console handler with colors
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        colorize=True
    )
    
    # File handler
    log_file = Path(settings.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        str(log_file),
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="10 MB",
        retention="1 week",
        compression="zip"
    )
    
    return logger