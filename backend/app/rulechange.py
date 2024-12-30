import json
import os
import sys


from schemas import AttributesScope
from utils import *
from helpers import (
    MqttTopic,
    logging,
    settings,
    get_channels,
    channel,
    Queue,
    SessionLocal,
)


def get_db():
    with SessionLocal() as db:
        db_api = Crud(db)
        return db_api


def save_telemetry(body):
    ts = body["ts"]
    payload = body["payload"]
    device_info = body["device_info"]
    entity_id = device_info["id"]
    key = payload["key"]
    value = payload["value"]
    status = db.insert_or_update_telemetry(str(entity_id), key, value, ts)


def save_attibute(body):
    last_update_ts = body["ts"]
    attribute_type = body["scope"]
    payload = body["payload"]
    device_info = body["device_info"]
    entity_id = device_info["id"]
    attribute_key = payload["key"]

    value = payload["value"]
    if type(value) is dict:
        value = json.dumps(value)
    status = db.insert_or_update_attribute(
        str(entity_id), "DEVICE", attribute_type, attribute_key, value, last_update_ts
    )

    if attribute_type == AttributesScope.SHARED_SCOPE:
        message = json.dumps(body)
        basic_publish(channel, Queue.ATTRIBUTE_RES, message)


def callback_telemetry(ch, method, properties, body):
    try:
        state = "START"
        body = body.decode("utf8").replace("'", '"')
        body = json.loads(body)
        # print(body)
        state = "INSERT"
        if method.routing_key == Queue.SAVE_TELEMETRY:
            save_telemetry(body)
        else:
            print(f" [x] {method.routing_key}:{body}")
        state = ""
        state = "DONE"
    except:
        logging.error(f"Worker Failed in stage {state.ljust(20, '-')}")
    finally:
        ch.basic_ack(method.delivery_tag)


def callback_attribute(ch, method, properties, body):
    try:
        state = "START"
        body = body.decode("utf8").replace("'", '"')
        body = json.loads(body)
        # print(body)
        state = "INSERT"
        if method.routing_key == Queue.SAVE_ATTRIBUTE:
            save_attibute(body)
        else:
            print(f" [x] {method.routing_key}:{body}")
        state = ""
        state = "DONE"
    except:
        logging.error(f"Worker Failed in stage {state.ljust(20, '-')}")
    finally:
        ch.basic_ack(method.delivery_tag)


db = get_db()


def main():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=Queue.SAVE_TELEMETRY, on_message_callback=callback_telemetry
    )
    channel.basic_consume(
        queue=Queue.SAVE_ATTRIBUTE, on_message_callback=callback_attribute
    )
    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    if not os.path.exists("../logs")
        os.mkdir("../logs")
    logging.basicConfig(
        filename="../logs/save_telemetry.log",
        filemode="a",
        format="%(levelname)s\t%(asctime)s\t%(message)s",
        level=logging.INFO,
    )
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
