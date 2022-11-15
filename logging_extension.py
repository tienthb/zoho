from logging.handlers import TimedRotatingFileHandler
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(threadName)-20.20s] — %(name)s — %(funcName)s:%(lineno)d — %(levelname)s — %(message)s",
    handlers=[
        TimedRotatingFileHandler("attendance.log", when="midnight", utc=True),
        logging.StreamHandler(sys.stdout),
    ],
)


def get_logger(name):
    logger = logging.getLogger(name)
    return logger