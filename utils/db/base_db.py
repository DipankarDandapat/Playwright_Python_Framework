from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union
from utils.logger import customLogger

log = customLogger()


class BaseDB(ABC):
    """Abstract base class for all database connectors"""

    @abstractmethod
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a query and return results"""
        pass

    @abstractmethod
    def execute_non_query(self, query: str, params: tuple = None) -> int:
        """Execute a query that doesn't return results (INSERT/UPDATE/DELETE)"""
        pass

    @abstractmethod
    def close(self):
        """Close the database connection"""
        pass

    @abstractmethod
    def clean_test_data(self, table_name: str, where_clause:str):
        """
        Clean up test data from specified table

        Args:
            table_name: Name of the table/container to clean
            where_clause: Either a single record (dict) needed for deletion
        """
        pass