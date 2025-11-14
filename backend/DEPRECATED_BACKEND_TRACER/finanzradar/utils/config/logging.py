import logging
import coloredlogs
from pathlib import Path

def init_logger(name: str = __name__, level: str = "INFO", log_file: str = None):
    """
    Initialize a logger with colored output.
    
    Args:
        name: Logger name.
        level: Logging level (default: INFO).
        log_file: Optional file path to also save logs.
        
    Returns:
        Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level.upper())

    # Remove any previous handlers (important if called multiple times)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Install coloredlogs
    coloredlogs.install(
        level=level.upper(),
        logger=logger,
        fmt='%(asctime)s [%(levelname)s] [%(filename)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    # Optional: also log to a file
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level.upper())
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
