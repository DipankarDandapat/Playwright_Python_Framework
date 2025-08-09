import psycopg2
from .base_db import BaseDB
from config.config import Config
import os
from utils.logger import customLogger
from psycopg2.sql import Composed

log = customLogger()


class PostgreSQLDB(BaseDB):
    def __init__(self):
        config = Config(os.getenv("ENV", "dev"))
        self.connection = psycopg2.connect(
            host=config.POSTGRES_HOST,
            database=config.POSTGRES_DB,
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD,
            port=config.POSTGRES_PORT

        )

        self.cursor = self.connection.cursor()

    def execute_query(self, query: str, params: tuple = None) -> list:
        self.cursor.execute(query, params or ())
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def execute_non_query(self, query: str, params: tuple = None) -> int:
        self.cursor.execute(query, params or ())
        self.connection.commit()
        return self.cursor.rowcount

    def close(self):
        if not self.connection.closed:
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
