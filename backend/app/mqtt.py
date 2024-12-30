import json
import sys
import os

# import threading
# import paho.mqtt as mqttc
import paho.mqtt.client as paho

from threading import Thread

from utils import *
from schemas import AttributesScope
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


def get_topic(msg):
    token: str = msg.topic.split("/")[0]
    topic: str = msg.topic[len(token) :]
    return topic, token


def save_telemetry(payload, device_info, ts):
    pass
    for item in payload.keys():
        msg = {
            "payload": {"key": item, "value": payload[item]},
            "ts": ts,
            "device_info": device_info,
        }
        msg = json.dumps(msg)
        basic_publish(Queue.SAVE_TELEMETRY, msg)


def save_attibute(payload, device_info, ts):
    pass

    for item in payload.keys():
        msg = {
            "payload": {"key": item, "value": payload[item]},
            "scope": AttributesScope.CLIENT_SCOPE.value,
            "ts": ts,
            "device_info": device_info,
        }
        msg = json.dumps(msg)
        basic_publish(Queue.SAVE_ATTRIBUTE, msg)


def attibute_req(msg, device_info, ts):
    basic_publish(Queue.ATTRIBUTE_REQ, msg)
    pass


def attibute_res(msg, device_info, ts):
    pass
    msg = json.dumps(msg)
    basic_publish(Queue.ATTRIBUTE_RES, msg)


db = get_db()


def message_handling(client, userdata, msg):
    if len(msg.topic) > 20:
        topic, token = get_topic(msg)
        payload = msg.payload.decode()
        if topic != MqttTopic.ATTRIBUTE_RES:
            try:
                payload = json.loads(payload)
                ts = timestamp()
                device_info = db.get_device_info_by_credential(token)
                # print(device_info)
                if device_info != False:
                    if topic == MqttTopic.TELEMETRY:
                        save_telemetry(payload, device_info, ts)
                    elif topic == MqttTopic.ATTRIBUTE:
                        save_attibute(payload, device_info, ts)
                    elif topic == MqttTopic.ATTRIBUTE_REQ:
                        print(topic)
                    else:
                        print(f"{msg.topic}: {msg.payload.decode()}")
            except:
                state = msg
                logging.error(f"Worker Failed in stage {state.ljust(20, '-')}")
            finally:
                pass


def callback(ch, method, properties, body):
    try:
        state = "START"
        body = body.decode("utf8").replace("'", '"')
        body = json.loads(body)
        credential = body["device_info"]["credential"]
        topic = f"{credential}{MqttTopic.ATTRIBUTE_RES.value}"
        key = body["payload"]["key"]
        value = body["payload"]["value"]
        msg = {key: value}
        # client.publish(topic, json.dumps(msg), 0)
        print(msg)
        state = "DONE"
        ch.basic_ack(method.delivery_tag)
    except:
        logging.error(f"Worker Failed in stage {state.ljust(20, '-')}")
    finally:
        pass


def rabbitmq():
    ch = get_channels()
    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(queue=Queue.ATTRIBUTE_RES, on_message_callback=callback)
    ch.start_consuming()


def mqtt():
    try:
        client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASS)
        if client.connect(settings.MQTT_HOST, settings.MQTT_PORT, 60) != 0:
            print("Couldn't connect to the mqtt broker")
            logging.error("Couldn't connect to the mqtt broker")
            sys.exit(1)
        client.subscribe("#")
        client.on_message = message_handling
        client.loop_forever()
    except:
        print("Caught an Exception, something went wrong...")
        client.disconnect()
        print("Disconnecting from the MQTT broker")
        mqtt()


if __name__ == "__main__":
    if not os.path.exists("../logs"):
        os.mkdir("../logs")
    logging.basicConfig(
        filename="../logs/mqtt.log",
        filemode="a",
        format="%(levelname)s\t%(asctime)s\t%(message)s",
        level=logging.INFO,
    )

    client = paho.Client(client_id=generate_uuid())
    try:
        t1 = Thread(target=rabbitmq)
        t2 = Thread(target=mqtt)
        t1.start()
        t2.start()
        print("Press CTRL+C to exit...")
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Disconnecting from the MQTT broker")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
