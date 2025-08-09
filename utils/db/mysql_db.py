import mysql.connector
from mysql.connector import Error
from .base_db import BaseDB
from config.config import Config
import os
from typing import List, Dict, Union
from utils.logger import customLogger

log = customLogger()


class MySQLDB(BaseDB):
    def __init__(self):
        config = Config(os.getenv("ENV", "dev"))
        self.connection = mysql.connector.connect(
            host=config.MYSQL_HOST,
            database=config.MYSQL_DB,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            port=config.MYSQL_PORT
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def execute_query(self, query: str, params: tuple = None) -> list:
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()

    def execute_non_query(self, query: str, params: tuple = None) -> int:
        self.cursor.execute(query, params or ())
        self.connection.commit()
        return self.cursor.rowcount

    def close(self):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()

    def clean_test_data(self, table_name: str, where_clause: str):
        try:
            if not table_name or not where_clause:
                log.warning("Table name or WHERE clause missing. No action taken.")
                return

            query = f"DELETE FROM {table_name} WHERE {where_clause}"

            deleted_count = self.execute_non_query(query)
            log.info(f"Deleted {deleted_count} row(s) from {table_name} where {where_clause}")

        except Exception as e:
            log.error(f"Error deleting record from {table_name}: {e}")
        finally:
            self.close()
