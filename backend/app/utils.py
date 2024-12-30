import json
import math
import time
import uuid
import random
import pika
import string
import sqlalchemy as sa
from sqlalchemy.sql import label
from sqlalchemy.orm import Session

# from sqlalchemy import desc, or_, func, text
from fastapi import HTTPException, status
from sqlalchemy.dialects import postgresql as pg

from schemas import AttributesScope, EntityTyppe
from models import *
from helpers import channel


def get_pages_records(data, offset_limit):
    offset, limit = offset_limit
    records, length = data
    return {
        "total_pages": math.ceil(length / limit),
        "total_elements": length,
        "has_next": offset + len(records) < length,
        "data": records,
    }


def get_offset_limit(page_size: int = 10, page: int = 0):
    if page_size <= 0:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Incorrect page link page size '{page_size}'. Page size must be greater than zero.",
        )
    if page < 0:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Incorrect page '{page}'. Page must be positive number.",
        )
    offset = page * page_size
    return offset, page_size


def timestamp():
    return round(time.time() * 1000)


def generate_uuid():
    return str(uuid.uuid4())


def generate_credentials():
    res = "".join(
        random.choices(string.ascii_letters, k=20)
    )  # initializing size of string
    return res


def basic_publish(channel, routing_key, message):
    channel.basic_publish(
        exchange="",
        routing_key=routing_key,
        body=str(message),
        properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
    )


class Crud:
    def __init__(self, db) -> None:
        self.db: Session = db

    def insert_or_update_attribute(
        self,
        entity_id,
        entity_type,
        attribute_type,
        attribute_key,
        value,
        last_update_ts,
    ):
        try:
            stmt = sa.text(
                """ 
                INSERT INTO attribute_kv (entity_id, entity_type, attribute_type, attribute_key, value, last_update_ts) 
                VALUES (:entity_id, :entity_type, :attribute_type, :attribute_key, :value, :last_update_ts)
                ON CONFLICT (entity_id, entity_type, attribute_type, attribute_key) DO UPDATE 
                SET value = excluded.value, 
                    last_update_ts = excluded.last_update_ts;
                """
            )

            params = {
                "entity_id": str(entity_id),
                "entity_type": entity_type,
                "attribute_type": attribute_type,
                "attribute_key": attribute_key,
                "value": value,
                "last_update_ts": last_update_ts,
            }
            self.db.execute(
                stmt,
                params,
            )
            self.db.commit()
            return True
        except:
            self.db.rollback()
            return False

    def insert_or_update_telemetry(self, entity_id, key, value, ts):
        try:
            stmt = sa.text(
                """
                INSERT INTO ts_kv (entity_id, key, value, ts)
                VALUES (:entity_id, :key, :value, :ts)
                ON CONFLICT (entity_id, key, ts) DO UPDATE
                SET value = excluded.value;
                """
            )
            params = {"entity_id": entity_id, "key": key, "value": value, "ts": ts}
            self.db.execute(stmt, params)
            self.db.commit()
            return True
        except:
            self.db.rollback()
            return False

    def update_telemetry(self, entity_id: str, key: str, ts: int, value: str):
        try:
            data = self.db.query(Telemetry)
            data = data.filter(
                Telemetry.key == str(key),
                Telemetry.entity_id == str(entity_id),
                Telemetry.ts == ts,
            )
            data = data.first()
            if data is None:
                return False
            data.value = str(value)
            self.db.commit()
            self.db.refresh(data)
            return {
                "entity_id": data.entity_id,
                "key": data.key,
                "ts": data.ts,
                "value": data.value,
            }
        except:
            self.db.rollback()
            return False

    def create_telemetry(self, entity_id: str, key: str, value: str):
        try:
            data = Telemetry(entity_id=str(entity_id), key=str(key), value=str(value))

            self.db.add(data)
            self.db.commit()
            self.db.refresh(data)
            return {
                "entity_id": data.entity_id,
                "key": data.key,
                "ts": data.ts,
                "value": data.value,
            }
        except:
            self.db.rollback()
            return False

    def get_oder_info(self, device_id: str, ts: str):
        data = self.db.query(
            Telemetry.entity_id,
            Telemetry.ts,
            label("value", Telemetry.value.cast(pg.JSON)),
        )
        data = data.filter(
            Telemetry.key == "order",
            Telemetry.entity_id == str(device_id),
            Telemetry.ts == ts,
        )
        data = data.first()
        return {"entity_id": data.entity_id, "ts": data.ts, "value": data.value}

    def delete_oder(self, device_id: str, ts: str):
        try:
            data = self.db.query(Telemetry)
            data = data.filter(
                Telemetry.key == "order",
                Telemetry.entity_id == str(device_id),
                Telemetry.ts == ts,
            )
            data = data.delete()
            self.db.commit()
            return True
        except:
            self.db.rollback()
            return False

    def get_oder_list(
        self,
        ids: list = [],
        propositions: list = [],
        shipping: list = [],
        username: list = [],
        phone: list = [],
        offset=None,
        limit=None,
    ):
        data = self.db.query(
            Telemetry.entity_id,
            Telemetry.ts,
            label("value", Telemetry.value.cast(pg.JSON)),
        )
        data = data.filter(Telemetry.key == "order")
        if ids:
            data = data.filter(Telemetry.entity_id.in_(tuple(ids)))
        if propositions:
            data = data.filter(
                Telemetry.value.cast(pg.JSON)["proposition"]
                .astext.cast(sa.String)
                .in_(tuple(propositions))
            )
        if shipping:
            data = data.filter(
                Telemetry.value.cast(pg.JSON)["shipping"]
                .astext.cast(sa.String)
                .in_(tuple(shipping))
            )
        if username:
            data = data.filter(
                Telemetry.value.cast(pg.JSON)["username"]
                .astext.cast(sa.String)
                .in_(tuple(username))
            )
        if phone:
            data = data.filter(
                Telemetry.value.cast(pg.JSON)["phone"]
                .astext.cast(sa.String)
                .in_(tuple(phone))
            )
        total = data.count()
        if offset != None and limit != None:
            data = data.offset(offset).limit(limit)
        data = data.all()
        return [
            {"entity_id": item.entity_id, "ts": item.ts, "value": item.value}
            for item in data
        ], total

    def delete_relation_by_from_id(self, from_id: str = None, from_type: str = None):
        try:
            data = self.db.query(Relation)
            data = data.filter(
                Relation.from_id == str(from_id), Relation.from_type == str(from_type)
            )
            data = data.delete()
            self.db.commit()
            return True
        except:
            self.db.rollback()
            return False

    def delete_relation_by_to_id(self, to_id: str = None, to_type: str = None):
        try:
            data = self.db.query(Relation)
            data = data.filter(
                Relation.to_id == str(to_id), Relation.to_type == str(to_type)
            )
            data = data.delete()
            self.db.commit()
            return True
        except:
            self.db.rollback()
            return False

    def find_relation(
        self,
        from_id: str = None,
        from_type: str = None,
        to_id: str = None,
        to_type: str = None,
        relation_type: str = None,
        relation_type_group: str = None,
    ):
        data = self.db.query(Relation)
        if from_id and from_type:
            data = data.filter(
                Relation.from_id == str(from_id), Relation.from_type == str(from_type)
            )
        if to_id and to_type:
            data = data.filter(
                Relation.to_id == str(to_id), Relation.to_type == str(to_type)
            )
        if relation_type:
            data = data.filter(Relation.relation_type == str(relation_type))
        if relation_type_group:
            data = data.filter(Relation.relation_type_group == str(relation_type_group))

        data = data.all()
        return [
            {
                "from_id": item.from_id,
                "from_type": item.from_type,
                "to_id": item.to_id,
                "to_type": item.to_type,
                "relation_type": item.relation_type,
                "relation_type_group": item.relation_type_group,
                "additional_info": item.additional_info,
            }
            for item in data
        ]

    def delete_relation(
        self,
        from_id: str,
        from_type: str,
        to_id: str,
        to_type: str,
        relation_type: str,
        relation_type_group: str,
    ):
        try:
            data = self.db.query(Relation)
            data = data.filter(
                Relation.from_id == str(from_id),
                Relation.from_type == str(from_type),
                Relation.to_id == str(to_id),
                Relation.to_type == str(to_type),
                Relation.relation_type == str(relation_type),
                Relation.relation_type_group == str(relation_type_group),
            )
            data = data.delete()
            self.db.commit()
            return True
        except:
            self.db.rollback()
            return False

    def create_relation(
        self,
        from_id: str,
        from_type: str,
        to_id: str,
        to_type: str,
        relation_type: str,
        relation_type_group: str,
    ):
        try:
            data = Relation(
                from_id=str(from_id),
                from_type=str(from_type),
                to_id=str(to_id),
                to_type=str(to_type),
                relation_type=str(relation_type),
                relation_type_group=str(relation_type_group),
            )
            self.db.add(data)
            self.db.commit()
            self.db.refresh(data)
            return {
                "from_id": data.from_id,
                "from_type": data.from_type,
                "to_id": data.to_id,
                "to_type": data.to_type,
                "relation_type": data.relation_type,
                "relation_type_group": data.relation_type_group,
            }
        except:
            self.db.rollback()
            return False

    def get_atribute_value(self, id: str, scope: str = None, keys: list = []):
        data = self.db.query(Attribute)
        data = data.filter(
            Attribute.entity_id == str(id),
            # Attribute.attribute_key.in_(tuple(keys)),
            #    or_(Attribute.attribute_type == str(item)
            #    for item in keys)
        )
        if scope != None:
            data = data.filter(
                Attribute.attribute_type == str(scope),
            )
        if keys != []:
            data = data.filter(
                Attribute.attribute_key.in_(tuple(keys)),
            )
        data = data.all()
        data = [
            {
                "attribute_key": item.attribute_key,
                "attribute_type": item.attribute_type,
                "value": item.value,
                "ts": item.last_update_ts,
            }
            for item in data
        ]
        return data

    def get_atribute_keys(self, id: str, scope: str):
        data = self.db.query(Attribute.attribute_key)
        data = data.filter(
            Attribute.entity_id == str(id), Attribute.attribute_type == str(scope)
        )
        data = data.distinct()
        data = data.all()
        return [item.attribute_key for item in data]

    def delete_attibute_keys(self, id: str, scope: str, keys: list):
        try:
            data = self.db.query(Attribute)
            data = data.filter(
                Attribute.entity_id == str(id),
                Attribute.attribute_type == str(scope),
                Attribute.attribute_key.in_(tuple(keys)),
            )
            data = data.delete()
            self.db.commit()
            return True
        except:
            self.db.rollback()
            return False

    def detele_attribute(self, entity_id: str):
        try:
            data = self.db.query(Attribute)
            data = data.filter(Attribute.id == str(entity_id))
            data = data.delete()
            self.db.commit()
            return True
        except:
            self.db.rollback()
            return False

    def detele_telemetry(self, entity_id: str):
        try:
            data = self.db.query(Telemetry)
            data = data.filter(Telemetry.entity_id == str(entity_id))
            data = data.delete()
            self.db.commit()
            return True
        except:
            self.db.rollback()
            return False

    def create_asset(self, name: str, type: str):
        try:
            data = Asset(name=str(name), type=str(type))
            self.db.add(data)
            self.db.commit()
            self.db.refresh(data)
            return {
                "id": str(data.id),
                "created_time": data.created_time,
                "additional_info": data.additional_info,
                "type": data.type,
                "name": data.name,
            }
        except:
            self.db.rollback()
            return False

    def get_asset_info(self, id: str):
        data = self.db.query(Asset)
        data = data.filter(Asset.id == str(id))
        data = data.first()
        if data == None:
            return False
        return {
            "id": str(data.id),
            "created_time": data.created_time,
            "additional_info": data.additional_info,
            "type": data.type,
            "name": data.name,
        }

    def delete_asset(self, id: str):
        try:
            data = self.db.query(Asset)
            data = data.filter(Asset.id == str(id))
            data = data.delete()
            self.db.commit()
            self.detele_attribute(id)
            self.detele_telemetry(id)
            self.delete_relation_by_from_id(id, EntityTyppe.ASSET.value)
            self.delete_relation_by_to_id(id, EntityTyppe.ASSET.value)
            return True
        except:
            self.db.rollback()
            return False

    def get_asset_list(self, offset=None, limit=None):
        data = self.db.query(Asset)
        total = data.count()
        if offset != None and limit != None:
            data = data.offset(offset).limit(limit)
        data = data.all()
        return [
            {
                "id": str(item.id),
                "created_time": item.created_time,
                "additional_info": item.additional_info,
                "type": item.type,
                "name": item.name,
            }
            for item in data
        ], total

    def delete_device(self, id: str):
        try:
            data = self.db.query(Device)
            data = data.filter(Device.id == str(id))
            data = data.delete()
            self.db.commit()
            self.detele_attribute(id)
            self.detele_telemetry(id)
            self.delete_relation_by_from_id(id, EntityTyppe.DEVICE.value)
            self.delete_relation_by_to_id(id, EntityTyppe.DEVICE.value)
            return True
        except:
            self.db.rollback()
            return False

    def create_device(self, name: str, credential: str, additional_info: str):
        try:
            data = Device(
                name=str(name),
                additional_info=additional_info,
                credential=str(credential),
            )
            self.db.add(data)
            self.db.commit()
            self.db.refresh(data)
            return {
                "id": str(data.id),
                "created_time": data.created_time,
                "additional_info": data.additional_info,
                "type": data.type,
                "name": data.name,
                "credential": data.credential,
            }
        except:
            self.db.rollback()
            return False

    def get_device_info_by_credential(self, credential: str):
        data = self.db.query(Device)
        data = data.filter(Device.credential == str(credential))
        data = data.first()
        if data == None:
            return False
        return {
            "id": str(data.id),
            "name": data.name,
            "type": data.type,
            "created_time": data.created_time,
            "credential": data.credential,
        }

    def get_device_info(self, id: str):
        data = self.db.query(Device)
        data = data.filter(Device.id == str(id))
        data = data.first()
        if data == None:
            return False
        return {
            "id": str(data.id),
            "created_time": data.created_time,
            "additional_info": data.additional_info,
            "type": data.type,
            "name": data.name,
            "credential": data.credential,
        }

    def get_device_list(self, offset=None, limit=None):
        data = self.db.query(Device)
        total = data.count()
        if offset != None and limit != None:
            data = data.offset(offset).limit(limit)
        data = data.all()
        return [
            {
                "id": str(item.id),
                "created_time": item.created_time,
                "additional_info": item.additional_info,
                "type": item.type,
                "name": item.name,
                "credential": item.credential,
            }
            for item in data
        ], total


class Api:
    def __init__(self) -> None:
        pass
