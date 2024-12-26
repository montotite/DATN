
import logging
from enum import Enum
import os
import urllib.parse
from typing import Optional
from dotenv import load_dotenv
import pika
from sqlalchemy import create_engine
from pydantic_settings import BaseSettings
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
load_dotenv()


class Settings(BaseSettings):
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: Optional[int] = os.getenv("DB_PORT") or 5432
    DB_USER: str = os.getenv("DB_USER")
    DB_PASS: str = os.getenv("DB_PASS")
    DB_NAME: str = os.getenv("DB_NAME")
    DATABASE_URL: Optional[str] \
        = f"postgresql://{DB_USER}:{urllib.parse.quote(DB_PASS)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    RB_HOST: str = os.getenv("RB_HOST") or ""
    RB_PORT: Optional[int] = os.getenv("RB_PORT") or 5672
    RB_VHOST: str = os.getenv("RB_VHOST") or "/"
    RB_USER: str = os.getenv("RB_USER") or ""
    RB_PASS: str = os.getenv("RB_PASS") or ""

    MQTT_HOST: Optional[str] = os.getenv("MQTT_HOST")
    MQTT_PORT: Optional[int] = os.getenv("MQTT_PORT") or 1883
    MQTT_USER: Optional[str] = os.getenv("MQTT_USER")
    MQTT_PASS: Optional[str] = os.getenv("MQTT_PASS")

    class Config:
        env_file = ".env"


class MqttTopic(str, Enum):
    TELEMETRY = '/devices/me/telemetry'
    ATTRIBUTE = '/devices/me/attributes'
    ATTRIBUTE_REQ = '/devices/me/attributes/request'
    ATTRIBUTE_RES = '/devices/me/attributes/response'
    RPC_REQ = '/devices/me/rpc/response'
    RPC_RES = '/devices/me/rpc/response'

    @staticmethod
    def list():
        return list(map(lambda c: c.value, MqttTopic))


class Queue(str, Enum):
    SAVE_ATTRIBUTE = 'save_attibute'
    SAVE_TELEMETRY = 'save_telemetry'
    ATTRIBUTE_REQ = 'attibute_req'
    ATTRIBUTE_RES = 'attibute_res'

    @staticmethod
    def list():
        return list(map(lambda c: c.value, Queue))


settings = Settings()

Base = declarative_base()
engine = create_engine(url=settings.DATABASE_URL,
                       pool_size=10,
                       max_overflow=20)
SessionLocal = sessionmaker(autocommit=False,
                            autoflush=False,
                            bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def gen_rb_con():
    credentials = pika.PlainCredentials(settings.RB_USER, settings.RB_PASS)
    connect = pika.ConnectionParameters(host=settings.RB_HOST,
                                        port=settings.RB_PORT,
                                        virtual_host=settings.RB_VHOST,
                                        credentials=credentials,
                                        heartbeat=0)
    rb_con = pika.BlockingConnection(connect)
    return rb_con


def get_channels():
    rb_con = gen_rb_con()
    channel = rb_con.channel()
    for item in Queue.list():
        channel.queue_declare(queue=item)
    return channel


channel = get_channels()
