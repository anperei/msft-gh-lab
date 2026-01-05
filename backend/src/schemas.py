from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DeviceBase(BaseModel):
    """Base schema for device"""
    name: str = Field(..., min_length=1, max_length=255, description="Device name")
    assigned_to: Optional[str] = Field(None, max_length=255, description="Person or department assigned to")


class DeviceCreate(DeviceBase):
    """Schema for creating a device"""
    pass


class DeviceUpdate(BaseModel):
    """Schema for updating a device"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Device name")
    assigned_to: Optional[str] = Field(None, max_length=255, description="Person or department assigned to")


class DeviceResponse(DeviceBase):
    """Schema for device response"""
    id: str  # Cosmos DB uses string IDs
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
