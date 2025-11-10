import cryptography
import logging
import sqlite3
from typing import Dict, Any, overload, Union
import bcrypt
# prepare Log file
LOG_FILE = 'LOG.log'
logging.basicConfig(filename=LOG_FILE,level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')

def write_to_log(msg) -> None:
    logging.info(msg)
    print(msg)

