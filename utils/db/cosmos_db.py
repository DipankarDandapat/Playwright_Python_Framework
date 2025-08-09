from azure.cosmos import CosmosClient
from .base_db import BaseDB
from config.config import Config
import os
from typing import List, Dict, Union
from utils.logger import customLogger

log = customLogger()

class CosmosDB(BaseDB):
    def __init__(self):
        config = Config(os.getenv("ENV", "dev"))
        self.client = CosmosClient(
            config.COSMOS_DB_HOST,
            credential=config.COSMOS_DB_KEY
        )
        self.database = self.client.get_database_client(config.COSMOS_DB_NAME)
        self.container = self.database.get_container_client(config.COSMOS_DB_CONTAINER)

    def execute_query(self, query: str, params: tuple = None) -> list:
        items = list(self.container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        return items

    def execute_non_query(self, query: str, params: tuple = None) -> int:
        # Cosmos DB doesn't return row count for modifications
        self.container.upsert_item(params)
        return 1

    def close(self):
        # Cosmos client doesn't need explicit closing
        pass



    def clean_test_data(self, table_name: str, where_clause: str):
        try:
            if not table_name or not where_clause:
                log.warning("Table name or WHERE clause missing. No action taken.")
                return

            container = self.database.get_container_client(table_name)

            # Query items matching the where_clause
            query = f"SELECT * FROM c WHERE {where_clause}"
            items_to_delete = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))

            if not items_to_delete:
                log.info(f"No items found in {table_name} for condition: {where_clause}")
                return

            deleted_count = 0
            for item in items_to_delete:
                try:
                    # Partition key depends on your setup; here assuming 'id' is the key
                    container.delete_item(item['id'], partition_key=item['id'])
                    deleted_count += 1
                except Exception as e:
                    log.error(f"Error deleting item {item.get('id')} from {table_name}: {e}")

            log.info(f"Deleted {deleted_count} item(s) from {table_name} where {where_clause}")

        except Exception as e:
            log.error(f"Error deleting record(s) from {table_name}: {e}")
        finally:
            self.close()
