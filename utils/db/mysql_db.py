import mysql.connector
from mysql.connector import Error
from .base_db import BaseDB
import os
from typing import List, Dict, Union
from utils.logger import customLogger
log = customLogger()


class MySQLDB(BaseDB):
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            database=os.getenv("MYSQL_DB"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            port=os.getenv("MYSQL_PORT"),
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
