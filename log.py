import logging
import os
from datetime import date, timedelta

# Creating day for naming
day = date.today() - timedelta(days=1)
day = day.strftime("%m-%d-%Y")

# Find current path
path = os.path.dirname(os.path.abspath(__file__))

# Creates debug.log which shows all info to spot failures
logging.basicConfig(filename=path+f"\\logs\\{day}debug.log", encoding='utf-8', level=logging.DEBUG)

# Code to create new logs
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

# Created new log 'log.log'
# log.log is used to add trackers and track the script
# To access in other files 'from niu import logger'
# To create log messages 'logger.info("your message")'
logger = setup_logger('short_logger', path+f"\\logs\\{day}log.log")
