import sys
from pathlib import Path

import structlog
from loguru import logger

from config import config

"""
Loguru for console and simple file logging
+ scructlog for JSON logging, than sucked to Grafana
"""

logger.remove(0)  # removing default loguru logger and replace it with a better formatted variant
logger.add(sys.stderr, level=config.LOG_LEVEL, format="<level>{message}</level>", colorize=True)

"""
Optional loguru file logger with rotation can be added with following code:

logger.add(
    config.LOG_FILE_PATH,
    level="DEBUG",
    rotation="1 MB",
    retention="10 days",
    format="{time:YYYY-MM-DD at HH:mm:ss} {level} {message}",
)
"""

# Configure the logger for writing JSON logs to a file
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.WriteLoggerFactory(file=Path(config.LOG_DIR).joinpath("api.log").open("a")),
)

file_logger = structlog.get_logger()


def log(message: str, level: str = "info", **kwars) -> None:
    """Main application-wide logging function
    Can accept a single string or a dictionary of additional data

    Then it sends it to both console and file loggers

    """
    match level.lower():
        case "debug":
            logger.debug(message, **kwars)
            file_logger.debug(message, **kwars)
        case "warn" | "warning":
            logger.warning(message, **kwars)
            file_logger.warning(message, **kwars)
        case "error":
            logger.error(message, **kwars)
            file_logger.error(message, **kwars)
        case "critical":
            logger.critical(message, **kwars)
            file_logger.critical(message, **kwars)
        case _:
            logger.info(message, **kwars)
            file_logger.info(message, **kwars)
