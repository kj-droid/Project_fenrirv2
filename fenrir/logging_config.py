# fenrir/logging_config.py
import logging
import sys
from logging.handlers import RotatingFileHandler
from colorama import Fore, Style, init

init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """A custom log formatter that adds color to log levels."""
    LOG_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
    }

    def format(self, record):
        log_color = self.LOG_COLORS.get(record.levelno)
        record.levelname = f"{log_color}{record.levelname:<8}{Style.RESET_ALL}"
        return super().format(record)

def setup_logging(log_level=logging.INFO):
    """Configures and returns a logger instance."""
    logger = logging.getLogger("fenrir")
    logger.setLevel(log_level)
    logger.propagate = False

    if logger.hasHandlers():
        logger.handlers.clear()

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_format = "%(levelname)s - %(message)s"
    console_formatter = ColoredFormatter(console_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File Handler
    file_handler = RotatingFileHandler("fenrir.log", maxBytes=5*1024*1024, backupCount=5)
    file_format = "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
    file_formatter = logging.Formatter(file_format)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger

log = setup_logging()
