"""
Cosmos DB client with lazy initialization and DefaultAzureCredential.
Uses system-assigned managed identity when running in Azure.
"""
import os
import logging
from typing import Optional

from azure.cosmos.aio import CosmosClient
from azure.cosmos import DatabaseProxy, ContainerProxy
from azure.identity.aio import DefaultAzureCredential

logger = logging.getLogger(__name__)

# Global client instance (lazy-loaded)
_cosmos_client: Optional[CosmosClient] = None
_credential: Optional[DefaultAzureCredential] = None


def get_cosmos_config() -> dict:
    """Get Cosmos DB configuration from environment variables."""
    return {
        "endpoint": os.environ.get("COSMOS_ENDPOINT", ""),
        "database_name": os.environ.get("COSMOS_DB_NAME", "inventory"),
        "devices_container": os.environ.get("COSMOS_DEVICES_CONTAINER", "devices"),
    }


async def get_cosmos_client() -> CosmosClient:
    """
    Get or create the Cosmos DB client using DefaultAzureCredential.
    Uses lazy initialization to avoid blocking at import time.
    """
    global _cosmos_client, _credential
    
    if _cosmos_client is None:
        config = get_cosmos_config()
        endpoint = config["endpoint"]
        
        if not endpoint:
            raise ValueError("COSMOS_ENDPOINT environment variable is required")
        
        logger.info(f"Initializing Cosmos DB client for endpoint: {endpoint}")
        
        # DefaultAzureCredential will use:
        # - Managed Identity in Azure Container Apps
        # - Azure CLI credentials locally
        _credential = DefaultAzureCredential()
        _cosmos_client = CosmosClient(endpoint, credential=_credential)
        
        logger.info("Cosmos DB client initialized successfully")
    
    return _cosmos_client


async def get_database() -> DatabaseProxy:
    """Get the Cosmos database proxy."""
    client = await get_cosmos_client()
    config = get_cosmos_config()
    return client.get_database_client(config["database_name"])


async def get_devices_container() -> ContainerProxy:
    """Get the devices container proxy."""
    database = await get_database()
    config = get_cosmos_config()
    return database.get_container_client(config["devices_container"])


async def close_cosmos_client():
    """Close the Cosmos DB client and release resources."""
    global _cosmos_client, _credential
    
    if _cosmos_client is not None:
        logger.info("Closing Cosmos DB client")
        await _cosmos_client.close()
        _cosmos_client = None
    
    if _credential is not None:
        await _credential.close()
        _credential = None
        
    logger.info("Cosmos DB resources released")
