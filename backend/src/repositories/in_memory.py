"""
In-memory device repository for testing and local development.
Provides same async interface as Cosmos DB repository without requiring Azure connectivity.
"""
import asyncio
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Optional

from src.schemas import DeviceCreate, DeviceUpdate, DeviceResponse

logger = logging.getLogger(__name__)

# Module-level storage and lock for thread-safe access
_devices: dict[str, dict] = {}
_devices_lock = asyncio.Lock()


def _doc_to_device(doc: dict) -> DeviceResponse:
    """Convert an in-memory document to a DeviceResponse."""
    return DeviceResponse(
        id=doc["id"],
        name=doc["name"],
        assigned_to=doc.get("assigned_to"),
        created_at=datetime.fromisoformat(doc["created_at"]),
        updated_at=datetime.fromisoformat(doc["updated_at"]),
    )


async def list_devices(skip: int = 0, limit: int = 100) -> List[DeviceResponse]:
    """List all devices with pagination."""
    async with _devices_lock:
        # Sort by created_at descending, then apply pagination
        sorted_devices = sorted(
            _devices.values(),
            key=lambda d: d["created_at"],
            reverse=True,
        )
        paginated = sorted_devices[skip : skip + limit]
        return [_doc_to_device(doc) for doc in paginated]


async def get_device(device_id: str) -> Optional[DeviceResponse]:
    """Get a device by ID."""
    async with _devices_lock:
        doc = _devices.get(device_id)
        if doc is None:
            return None
        return _doc_to_device(doc)


async def create_device(device: DeviceCreate) -> DeviceResponse:
    """Create a new device."""
    async with _devices_lock:
        now = datetime.now(timezone.utc).isoformat()
        device_id = str(uuid.uuid4())

        doc = {
            "id": device_id,
            "name": device.name,
            "assigned_to": device.assigned_to,
            "created_at": now,
            "updated_at": now,
        }

        _devices[device_id] = doc
        logger.info(f"Created device: {device_id}")
        return _doc_to_device(doc)


async def update_device(device_id: str, device: DeviceUpdate) -> Optional[DeviceResponse]:
    """Update an existing device."""
    async with _devices_lock:
        if device_id not in _devices:
            return None

        existing = _devices[device_id]

        # Update only the fields that were provided
        if device.name is not None:
            existing["name"] = device.name
        if device.assigned_to is not None:
            existing["assigned_to"] = device.assigned_to

        existing["updated_at"] = datetime.now(timezone.utc).isoformat()

        logger.info(f"Updated device: {device_id}")
        return _doc_to_device(existing)


async def delete_device(device_id: str) -> bool:
    """Delete a device by ID."""
    async with _devices_lock:
        if device_id not in _devices:
            return False

        del _devices[device_id]
        logger.info(f"Deleted device: {device_id}")
        return True
