from .cosmos_db import CosmosDB
from .mysql_db import MySQLDB
from .postgresql_db import PostgreSQLDB
import os


class DBFactory:
    @staticmethod
    def get_db(db_type: str):
        """Factory method to get database instance"""

        if db_type.lower() == "cosmos":
            return CosmosDB()
        elif db_type.lower() == "mysql":
            return MySQLDB()
        elif db_type.lower() == "postgresql":
            return PostgreSQLDB()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")