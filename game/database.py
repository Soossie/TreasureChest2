import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=os.environ.get('HOST'),
            port=3306,
            database=os.environ.get('DB_NAME'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASS'),
            autocommit=True,
            collation='utf8mb4_general_ci',
        )

    def get_conn(self):
        return self.conn
