from azure.cosmos import CosmosClient
from .base_db import BaseDB
import os
from typing import List, Dict, Any
from utils.logger import customLogger

log = customLogger()


class CosmosDB(BaseDB):
    def __init__(self):
        self.client = CosmosClient(
            os.getenv("COSMOS_DB_HOST"),
            credential=os.getenv("COSMOS_DB_KEY")
        )
        self.database = self.client.get_database_client(os.getenv("COSMOS_DB_NAME"))

    def _get_container(self, container_name: str):
        """Return container client dynamically"""
        return self.database.get_container_client(container_name)

    def execute_query(self, query: str, params: tuple = None, container_name: str = None) -> list:
        if not container_name:
            raise ValueError("Container name is required for CosmosDB query")

        container = self._get_container(container_name)
        items = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        return items

    def execute_non_query(self, query: str = None, params: dict = None, container_name: str = None) -> int:
        """
        For Cosmos DB, we ignore query and expect params to be a document (dict).
        """
        if not container_name:
            raise ValueError("Container name is required for CosmosDB non-query")

        if not isinstance(params, dict):
            raise ValueError("CosmosDB non-query expects 'params' as a dict (document to upsert)")

        container = self._get_container(container_name)
        container.upsert_item(params)
        return 1

    def close(self):
        # Cosmos client doesn't require explicit closing
        pass

    def clean_test_data(self, container_name: str, where_clause: str):
        try:
            if not container_name or not where_clause:
                log.warning("Container name or WHERE clause missing. No action taken.")
                return

            container = self._get_container(container_name)

            query = f"SELECT * FROM c WHERE {where_clause}"
            items_to_delete = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))

            if not items_to_delete:
                log.info(f"No items found in {container_name} for condition: {where_clause}")
                return

            deleted_count = 0
            for item in items_to_delete:
                try:
                    # Adjust partition key if different from 'id'
                    container.delete_item(item['id'], partition_key=item['id'])
                    deleted_count += 1
                except Exception as e:
                    log.error(f"Error deleting item {item.get('id')} from {container_name}: {e}")

            log.info(f"Deleted {deleted_count} item(s) from {container_name} where {where_clause}")

        except Exception as e:
            log.error(f"Error deleting record(s) from {container_name}: {e}")
        finally:
            self.close()
