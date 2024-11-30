from enum import Enum
from uuid import UUID
from pydantic import BaseModel
from typing import List, Optional, Union

class RecordList(BaseModel):
    total_pages: int
    total_elements: int
    has_next: bool


class DeviceInfo(BaseModel):
    id: Optional[UUID] = ""
    name: str
    credential: Optional[str] = ""
    created_time: Optional[int] = 0
    type: Optional[str] = ""
    additional_info: Optional[str] = ""


class DeviceList(RecordList):
    data: Optional[List[DeviceInfo]]
