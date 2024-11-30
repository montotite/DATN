import time
import uuid
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from helpers import Base


def timestamp():
    return round(time.time()*1000)


def generate_uuid():
    return str(uuid.uuid4())


class Device(Base):
    __tablename__ = 'device'