import time
import uuid
from sqlalchemy import desc, or_, func, text

from helpers import *


def timestamp():
    return round(time.time() * 1000)


def generate_uuid():
    return str(uuid.uuid4())


def basic_publish(routing_key, message):
    # message = ' '.join(sys.argv[1:]) or "Hello World!"

    channel.basic_publish(
        exchange="",
        routing_key=routing_key,
        body=str(message),
        properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
    )


def get_device_info_by_credential(token: str):
    with SessionLocal() as db:
        stmt = text(
            """
                SELECT *
                FROM "device"
                WHERE "credential" = :credential
                """
        )
        device_info = db.execute(stmt, params={"credential": str(token)}).fetchone()
        if device_info == None:
            return False
        return {
            "id": str(device_info.id),
            "created_time": device_info.created_time,
            "additional_info": device_info.additional_info,
            "type": device_info.type,
            "name": device_info.name,
            "credential": device_info.credential,
        }


def insert_or_update_attribute(
    entity_id, attribute_type, attribute_key, value, last_update_ts
):
    with SessionLocal() as db:
        stmt = text(
            """ 
            INSERT INTO attribute_kv (entity_id, attribute_type, attribute_key, value, last_update_ts) 
            VALUES (:entity_id, :attribute_type, :attribute_key, :value, :last_update_ts)
            ON CONFLICT (entity_id, attribute_type, attribute_key) DO UPDATE 
            SET value = excluded.value, 
                last_update_ts = excluded.last_update_ts;
            """
        )
        db.execute(
            stmt,
            {
                "entity_id": entity_id,
                "attribute_type": attribute_type,
                "attribute_key": attribute_key,
                "value": value,
                "last_update_ts": last_update_ts,
            },
        )
        db.commit()


def insert_or_update_telemetry(entity_id, key, value, ts):
    with SessionLocal() as db:
        stmt = text(
            """ 
            INSERT INTO ts_kv (entity_id, key, value, ts) 
            VALUES (:entity_id, :key, :value, :ts)
            ON CONFLICT (entity_id, key, ts) DO UPDATE 
            SET value = excluded.value;
            """
        )
        db.execute(stmt, {"entity_id": entity_id, "key": key, "value": value, "ts": ts})
        db.commit()
