import pandas
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status

from utils import *
from schemas import *
from helpers import get_db, Queue, get_channels

# Mock data
energy_data = [
    {"ts": 1732801051000, "energy": 100},
    {"ts": 1732887451000, "energy": 120},
    {"ts": 1732973851000, "energy": 150},
    {"ts": 1733060251000, "energy": 180},
    {"ts": 1733146651000, "energy": 200},
    {"ts": 1733233051000, "energy": 250},
    {"ts": 1733319451000, "energy": 300},
    {"ts": 1733405851000, "energy": 350},
    {"ts": 1733492251000, "energy": 400},
    {"ts": 1733578651000, "energy": 450},
    {"ts": 1733665051000, "energy": 500},
    {"ts": 1733751451000, "energy": 550},
    {"ts": 1733837851000, "energy": 600},
]

tags = [
    "RPC Controller",
    "Device",
    "Telemetry Controller",
    "Asset",
    "Relation",
    "Dashboard",
]
router = APIRouter()


@router.get(path="/asset", tags=[tags[3]], response_model=AssetList)
def get_asset_list(offset_limit=Depends(get_offset_limit), db=Depends(get_db)):
    offset, limit = offset_limit
    db = Crud(db)
    records, length = db.get_asset_list(offset, limit)
    data = records, length
    return get_pages_records(data, offset_limit)


@router.post(path="/asset", tags=[tags[3]], response_model=AssetInfo)
def create_asset(form_data: AssetInfo, db=Depends(get_db)):

    asset_info = Crud(db).create_asset(
        name=str(form_data.name), type=str(form_data.type)
    )
    if asset_info == False:
        raise HTTPException(400)
    return asset_info


@router.get(path="/asset/info", tags=[tags[3]], response_model=AssetInfo)
def get_asset_info(id: UUID, db=Depends(get_db)):
    asset_info = Crud(db).get_asset_info(str(id))
    return asset_info


@router.delete(
    path="/asset",
    tags=[tags[3]],
)
def delete_asset(id: UUID, db=Depends(get_db)):
    db = Crud(db)
    info = db.get_asset_info(id)
    if info == False:
        raise HTTPException(400)
    asset_id = info["id"]
    db.delete_asset(asset_id)
    return "OK"


@router.get(path="/device", tags=[tags[1]], response_model=DeviceList)
def get_device_list(offset_limit=Depends(get_offset_limit), db=Depends(get_db)):
    offset, limit = offset_limit
    db = Crud(db)
    records, length = db.get_device_list(offset, limit)
    data = records, length
    return get_pages_records(data, offset_limit)


@router.post(path="/device", tags=[tags[1]], response_model=DeviceInfo)
def create_device(form_data: DeviceInfo, db=Depends(get_db)):
    credential = generate_credentials()
    device_info = Crud(db).create_device(
        form_data.name, credential, form_data.additional_info
    )
    if device_info == False:
        raise HTTPException(400)
    device_id = device_info["id"]
    return get_device_info(device_id, db)


@router.get(path="/device/info", tags=[tags[1]], response_model=DeviceInfo)
def get_device_info(id: UUID, db=Depends(get_db)):
    db = Crud(db)
    info = db.get_device_info(id)
    return info


@router.delete(path="/device", tags=[tags[1]])
def delete_device(id: UUID, db=Depends(get_db)):
    db = Crud(db)
    info = db.get_device_info(id)
    if info == False:
        raise HTTPException(400)
    device_id = info["id"]
    db.delete_device(device_id)
    return "OK"


@router.get(path="/relation", tags=[tags[4]], response_model=RelationList)
def find_relation(
    from_id: UUID = None,
    from_type: EntityTyppe = None,
    to_id: UUID = None,
    to_type: EntityTyppe = None,
    type: str = None,
    type_group: str = None,
    db=Depends(get_db),
):
    """
    "entity_type": "ASSET" or "DEVICE"
    """
    if from_type:
        from_type = from_type.value
    if to_type:
        to_type = to_type.value

    data = Crud(db).find_relation(from_id, from_type, to_id, to_type, type, type_group)
    records = [
        {
            "from_id": {"id": item["from_id"], "entity_type": item["from_type"]},
            "to_id": {"id": item["to_id"], "entity_type": item["to_type"]},
            "type": item["relation_type"],
            "type_group": item["relation_type_group"],
            "additional_info": item["additional_info"],
        }
        for item in data
    ]
    return {
        "total_pages": 1,
        "total_elements": len(records),
        "has_next": False,
        "data": records,
    }


@router.post(path="/relation", tags=[tags[4]], response_model=RelationInfo)
def create_relation(form_data: RelationInfo, db=Depends(get_db)):
    """
    "entity_type": "ASSET" or "DEVICE"
    """
    if form_data.from_id.entity_type == EntityTyppe.ASSET.value:
        from_entity = get_asset_info(form_data.from_id.id, db)
    elif form_data.from_id.entity_type == EntityTyppe.DEVICE.value:
        from_entity = get_device_info(form_data.from_id.id, db)
    else:
        raise HTTPException(400)
    if form_data.to_id.entity_type == EntityTyppe.ASSET.value:
        to_entity = get_asset_info(form_data.to_id.id, db)
    elif form_data.to_id.entity_type == EntityTyppe.DEVICE.value:
        to_entity = get_device_info(form_data.to_id.id, db)
    else:
        raise HTTPException(400)
    if from_entity == False or to_entity == False:
        raise HTTPException(400)

    data = Crud(db).create_relation(
        from_id=str(from_entity["id"]),
        from_type=form_data.from_id.entity_type.value,
        to_id=str(to_entity["id"]),
        to_type=form_data.to_id.entity_type.value,
        relation_type=str(form_data.type),
        relation_type_group=str(form_data.type_group),
    )
    if data:
        return form_data
    raise HTTPException(400)


@router.delete(path="/relation", tags=[tags[4]])
def delete_relation(form_data: RelationInfo, db=Depends(get_db)):
    """'
    "entity_type": "ASSET" or "DEVICE"
    """
    data = Crud(db).delete_relation(
        from_id=str(form_data.from_id.id),
        from_type=form_data.from_id.entity_type.value,
        to_id=str(form_data.to_id.id),
        to_type=form_data.from_id.entity_type.value,
        relation_type=str(form_data.type),
        relation_type_group=str(form_data.type_group),
    )
    if data:
        return "OK"
    raise HTTPException(400)


@router.get(path="/plugins/telemetry/keys/attribute", tags=[tags[2]])
def get_attribute_keys(id: UUID, scope: AttributesScope, db=Depends(get_db)):
    keys = Crud(db).get_atribute_keys(str(id), str(scope.value))
    return keys


@router.delete(path="/plugins/telemetry/keys/attribute", tags=[tags[2]])
def delete_attribute_key(
    id: UUID, scope: AttributesScope, keys: str, db=Depends(get_db)
):
    keys = keys.split(",")
    if scope == AttributesScope.CLIENT_SCOPE:
        raise HTTPException(400)
    data = Crud(db).delete_attibute_keys(id, scope.value, keys)
    if data:
        return "OK"
    raise HTTPException(400)


@router.get(path="/plugins/telemetry/value/attribute", tags=[tags[2]])
def get_attribute_values(
    id: UUID, scope: AttributesScope, keys: str, db=Depends(get_db)
):
    keys = keys.split(",")
    data = Crud(db).get_atribute_value(str(id), scope.value, keys)

    return [
        {item["attribute_key"]: {"value": item["value"], "ts": item["ts"]}}
        for item in data
    ]


@router.post(path="/plugins/telemetry", tags=[tags[2]])
def save_atribute(
    id: UUID,
    scope: AttributesScope,
    body: dict,
    db=Depends(get_db),
):
    if scope == AttributesScope.CLIENT_SCOPE:
        raise HTTPException(400)
    device_info = Crud(db).get_device_info(id)
    if device_info == False:
        raise HTTPException(400)
    for item in body.keys():
        message = {
            "payload": {"key": item, "value": body[item]},
            "ts": timestamp(),
            "scope": scope.value,
            "device_info": device_info,
        }
        basic_publish(Queue.SAVE_ATTRIBUTE, json.dumps(message))
    return "OK"


@router.post(path="/plugins/telemetry/timeseries", tags=[tags[2]])
def save_telemetry(id: UUID, body: dict, db=Depends(get_db)):
    device_info = Crud(db).get_device_info(id)
    if device_info == False:
        raise HTTPException(400)
    for item in body.keys():
        message = {
            "payload": {item: body[item]},
            "ts": timestamp(),
            "device_info": device_info,
        }
        basic_publish(Queue.SAVE_TELEMETRY, json.dumps(message))
    return "OK"


# @router.post(path='/plugins/rpc',
#              tags=[tags[0]])
# def send_rpc_request(id: UUID):
#     return 'ok'
