"""
Device repository for CRUD operations.
Routes to in-memory repository in TEST_MODE, or Cosmos DB otherwise.
"""
import os

# Determine which repository backend to use
TEST_MODE = os.environ.get("TEST_MODE", "false").lower() == "true"

if TEST_MODE:
    from src.repositories.in_memory import (
        list_devices,
        get_device,
        create_device,
        update_device,
        delete_device,
    )
else:
    from src.repositories.cosmos_repo import (
        list_devices,
        get_device,
        create_device,
        update_device,
        delete_device,
    )

__all__ = [
    "list_devices",
    "get_device",
    "create_device",
    "update_device",
    "delete_device",
]
