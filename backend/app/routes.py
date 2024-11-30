import pandas
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status

from utils import *
from schemas import *
from helpers import get_db, Queue, get_channels


router = APIRouter()



@ router.get(path='/device', tags=[""], response_model=DeviceList)
def get_device_list(offset_limit=Depends(get_offset_limit), db=Depends(get_db)):

    
    records, length = [], 0
    data = records, length
    return get_pages_records(data, offset_limit)


@ router.post(path='/device', tags=[""], response_model=DeviceInfo)
def create_device(form_data: DeviceInfo,
                  db=Depends(get_db)):

    device_id = ""
    return get_device_info(device_id, db)


@ router.get(path='/device/info', tags=[""], response_model=DeviceInfo)
def get_device_info(id: UUID, db=Depends(get_db)):
    return 


@ router.delete(path='/device', tags=[""])
def delete_device(id: UUID, db=Depends(get_db)):

    return "OK"