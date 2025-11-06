import cryptography
import logging
import sqlite3
from typing import Dict
# prepare Log file
LOG_FILE = 'LOG.log'
logging.basicConfig(filename=LOG_FILE,level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')

def write_to_log(msg) -> None:
    logging.info(msg)
    print(msg)

class DataBase: 
    def __init__(self, path_url):
            self.url = path_url

    def Register(self, user: Dict[str, str] ) -> bool:
        with sqlite3.connect(self.url) as conn:
            cursor = conn.cursor()
            return cursor.execute(
                 "SELECT FROM users +" \
                 "WHERE username = :username" \
                 " AND password = :password ",user
                ) is not None
        

DB = DataBase("./Database.db")
