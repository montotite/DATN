import pandas
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status

from utils import *
from schemas import *
from helpers import get_db, Queue, get_channels, channel

# Mock data
energy_data = [
    {"ts": 1735668000000, "energy": 14},
    {"ts": 1735750800000, "energy": 16},
    {"ts": 1735837200000, "energy": 15},
    {"ts": 1735923600000, "energy": 1},
]

tags = [
    "RPC Controller",
    "Device",
    "Telemetry Controller",
    "Asset",
    "Relation",
    "Dashboard",
    "Alarm",
]
router = APIRouter()


@router.get(path="/alarm", tags=[tags[6]])
def get_alarm_list(offset_limit=Depends(get_offset_limit), db=Depends(get_db)):
    data = [
        {
            "id": "179cd5ad-b30b-407c-a2e0-cb0ee87996a9",
            "name": f"Tiêu thụ điện vượt ngưỡng",
            "created_time": 1735731422000,
            "type": None,
            "value": {"value": 14, "setting": 5},
            "status": "Đã xem",
            "additional_info": '{"description": "aaaa",}',
        },
        {
            "id": "179cd5ad-b30b-407c-a2e0-cb0ee87996a9",
            "name": f"Tiêu thụ điện vượt ngưỡng",
            "created_time": 1735821422000,
            "type": None,
            "value": {"value": 16, "setting": 5},
            "status": "Đã xem",
            "additional_info": '{"description": "aaaa",}',
        },
        {
            "id": "179cd5ad-b30b-407c-a2e0-cb0ee87996a9",
            "name": f"Tiêu thụ điện vượt ngưỡng",
            "created_time": 1735907822000,
            "type": None,
            "value": {"value": 15, "setting": 5},
            "status": "Đã xem",
            "additional_info": '{"description": "aaaa",}',
        },
    ]
    # for item in range(0, 2):
    #     data.append(
    #         {
    #             "id": "179cd5ad-b30b-407c-a2e0-cb0ee87996a9",
    #             "name": f"Tiêu thụ điện vượt ngưỡng",
    #             "created_time": 1734968314675,
    #             "type": None,
    #             "value": {"value": random.randint(5, 10), "setting": 5},
    #             "status": "Đã xem",
    #             "additional_info": '{"description": "aaaa",}',
    #         }
    #     )
    return {
        "total_pages": 1,
        "total_elements": 1,
        "has_next": False,
        "data": data,
    }


@router.get(path="/dashboard/month", tags=[tags[5]])
def get_dashboard_month(db=Depends(get_db)):
    return energy_data


@router.get(path="/dashboard/summary", tags=[tags[5]])
def get_dashboard_summary(db=Depends(get_db)):
    return {
        "today": {"cons": 1, "cost": 1746},
        "month": {"cons": 46, "cost": 80316},
        "year": {"cons": 46, "cost": 80316},
        "total": {"cons": 46, "cost": 80316},
    }
    # return {
    #     "today": {"cons": random.randint(3, 1000), "cost": random.randint(3, 1000)},
    #     "month": {"cons": random.randint(3, 1000), "cost": random.randint(3, 1000)},
    #     "year": {"cons": random.randint(3, 1000), "cost": random.randint(3, 1000)},
    #     "total": {"cons": random.randint(3, 1000), "cost": random.randint(3, 1000)},
    # }


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
    for item in records:
        item["attrbutes"] = {}
        for attribute in db.get_atribute_value(item["id"]):
            item["attrbutes"][attribute["attribute_type"]] = attribute
            item["attrbutes"][attribute["attribute_type"]].pop("attribute_type")
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
    id: UUID, scope: AttributesScope = None, keys: str = None, db=Depends(get_db)
):
    if keys != None:
        keys = keys.split(",")
    data = Crud(db).get_atribute_value(str(id), scope, keys)
    rs = {}
    for item in data:
        if rs.get(item["attribute_type"]) == None:
            rs[item["attribute_type"]] = []
        rs[item["attribute_type"]].append(
            {item["attribute_key"]: {"value": item["value"], "ts": item["ts"]}}
        )
    return rs


# @router.get(path="/plugins/telemetry/value/timeseries", tags=[tags[2]])
# def get_timeseries_values(id: UUID, keys: str = None, db=Depends(get_db)):
#     if keys != None:
#         keys = keys.split(",")
#     data = Crud(db).get_timeseries_value(str(id), keys)
#     # rs = {}
#     # for item in data:
#     #     if rs.get(item["attribute_type"]) == None:
#     #         rs[item["attribute_type"]] = []
#     #     rs[item["attribute_type"]].append(
#     #         {item["attribute_key"]: {"value": item["value"], "ts": item["ts"]}}
#     #     )
#     return data


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
        basic_publish(channel, Queue.SAVE_ATTRIBUTE, json.dumps(message))
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
        basic_publish(channel, Queue.SAVE_TELEMETRY, json.dumps(message))
    return "OK"


# @router.post(path='/plugins/rpc',
#              tags=[tags[0]])
# def send_rpc_request(id: UUID):
#     return 'ok'
