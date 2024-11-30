
import json
import math
import time
import uuid
import random
import pika
import string
from sqlalchemy.orm import Session
from fastapi import HTTPException,  status
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.sql import label
import sqlalchemy as sa

from model import *
from helpers import channel


def timestamp():
    return round(time.time()*1000)


def generate_uuid():
    return str(uuid.uuid4())


def generate_credentials():
    res = ''.join(random.choices(string.ascii_letters,
                                 k=20))  # initializing size of string
    return res


def basic_publish(routing_key, message):
    channel.basic_publish(exchange='',
                          routing_key=routing_key,
                          body=str(message),
                          properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent))
    

class Crud:
    def __init__(self, db) -> None:
        self.db: Session = db

    def delete_device(self, id: str):
        try:
            
            return True
        except:
            self.db.rollback()
            return False

    def create_device(self, name: str, credential: str):
        try:
            return
        except:
            self.db.rollback()
            return False

    def get_device_info(self, id: str):
        return

    def get_device_list(self, offset=None, limit=None):
        return