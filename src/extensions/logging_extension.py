from logging.handlers import TimedRotatingFileHandler
import logging
import sys
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — [%(threadName)-20.20s] — %(name)s — %(funcName)s:%(lineno)d — %(levelname)s — %(message)s",
    handlers=[
        TimedRotatingFileHandler("attendance.log", when="midnight", utc=True),
        logging.StreamHandler(sys.stdout),
    ],
)


def get_logger(name):
    file_name = os.getcwd() + name
    logger = logging.getLogger(name)
    logging.basicConfig(filename=file_name)
    return logger