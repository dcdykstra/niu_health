"""
Config INI helpers and Logging helper
"""
import logging
import os
from datetime import date, timedelta

from tokenize import String
from configparser import ConfigParser


class ConfigIni():
    """Gets information from config.ini file"""
    def __init__(self) -> None:
        path = os.path.dirname(os.path.abspath(__file__))
        local_config = ConfigParser()
        local_config.read(os.path.join(path, "config.ini"))
        userinfo = local_config["USERINFO"]
        self.outputdir = userinfo["datadir"]
        self.loginid = userinfo["loginid"]
        self.loginpassword = userinfo["password"]
        self.drivefolderid = userinfo["driveid"]
        self.currentpath = path
        self.daysago = int(userinfo["daysago"])

def mkdir_ifnotexist(path: String):
    """Created the folder if it doesn't exist"""
    if not os.path.exists(path):
        os.mkdir(path)


# Create data output folders based on config
config = ConfigIni()
mkdir_ifnotexist(config.outputdir)
logsFolderPath = os.path.join(config.outputdir, "logs")
mkdir_ifnotexist(logsFolderPath)

# Creating day for naming
day = date.today() - timedelta(days=config.daysago)
day = day.strftime("%m-%d-%Y")

# Creates debug.log which shows all info to spot failures
logging.basicConfig(filename=os.path.join(logsFolderPath, f"{day}debug.log"),
    encoding='utf-8', level=logging.DEBUG)

# Code to create new logs
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    local_logger = logging.getLogger(name)
    local_logger.setLevel(level)
    local_logger.addHandler(handler)

    return local_logger

# Created new log 'log.log'
# log.log is used to add trackers and track the script
# To access in other files 'from niu import logger'
# To create log messages 'logger.info("your message")'

logger = setup_logger('short_logger', os.path.join(logsFolderPath, f"{day}log.log"))
