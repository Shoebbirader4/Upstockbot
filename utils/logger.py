from loguru import logger
import sys
from pathlib import Path

def setup_logger(log_path: str = "./logs", log_level: str = "INFO"):
    Path(log_path).mkdir(parents=True, exist_ok=True)
    
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=log_level
    )
    
    logger.add(
        f"{log_path}/trading_{{time:YYYY-MM-DD}}.log",
        rotation="00:00",
        retention="30 days",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}"
    )
    
    logger.add(
        f"{log_path}/errors_{{time:YYYY-MM-DD}}.log",
        rotation="00:00",
        retention="90 days",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}"
    )
    
    return logger

log = setup_logger()
