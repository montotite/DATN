from enum import Enum
from uuid import UUID
from pydantic import BaseModel
from typing import List, Optional, Union


class EntityTyppe(str, Enum):
    ASSET = 'ASSET'
    ASSET_PROFILE = 'ASSET_PROFILE'
    DEVICE = 'DEVICE'
    DEVICE_PROFILE = 'DEVICE_PROFILE'
    ALARM = 'ALARM'
    USER = 'USER'


class AttributesScope(str, Enum):
    SERVER_SCOPE = 'SERVER_SCOPE'
    SHARED_SCOPE = 'SHARED_SCOPE'
    CLIENT_SCOPE = 'CLIENT_SCOPE'


class EntityId(BaseModel):
    id: UUID
    entity_type: EntityTyppe


class RecordList(BaseModel):
    total_pages: int
    total_elements: int
    has_next: bool


class OrderInfo(BaseModel):
    device_id: Optional[str] = None
    proposition: str
    create_time: Optional[int] = None
    shipping: Optional[str]
    username: Optional[str]
    phone: Optional[str]
    token: Optional[str]
    send_time: Optional[int]
    receive_time: Optional[int]


class OrderList(RecordList):
    data: Optional[List[OrderInfo]]


class RelationInfo(BaseModel):
    from_id: EntityId
    to_id: EntityId
    type: Optional[str] = "Contains"
    type_group: Optional[str] = "COMMON"
    additional_info: Optional[str] = ""


class RelationList(RecordList):
    data: Optional[List[RelationInfo]]


class AssetInfo(BaseModel):
    id: Optional[UUID] = ""
    name: str
    type: str = "Area"
    created_time: Optional[int] = 0
    additional_info: Optional[str] = ""


class AssetList(RecordList):
    data: Optional[List[AssetInfo]]


class DeviceInfo(BaseModel):
    id: Optional[UUID] = ""
    name: str
    credential: Optional[str] = ""
    created_time: Optional[int] = 0
    type: Optional[str] = ""
    additional_info: Optional[str] = ""
    attrbutes: Optional[dict] = {}


class DeviceList(RecordList):
    data: Optional[List[DeviceInfo]]
