import time
import uuid
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from helpers import Base


def timestamp():
    return round(time.time() * 1000)


def generate_uuid():
    return str(uuid.uuid4())


class Relation(Base):
    __tablename__ = "relation"
    from_id = sa.Column(sa.UUID(), autoincrement=False, nullable=False)
    from_type = sa.Column(sa.VARCHAR(length=255), autoincrement=False, nullable=False)
    to_id = sa.Column(sa.UUID(), autoincrement=False, nullable=False)
    to_type = sa.Column(sa.VARCHAR(length=255), autoincrement=False, nullable=False)
    relation_type_group = sa.Column(
        sa.VARCHAR(length=255), autoincrement=False, nullable=False
    )
    relation_type = sa.Column(
        sa.VARCHAR(length=255), autoincrement=False, nullable=False
    )
    additional_info = sa.Column(sa.VARCHAR(), autoincrement=False, nullable=True)

    sa.PrimaryKeyConstraint(
        from_id,
        from_type,
        relation_type_group,
        relation_type,
        to_id,
        to_type,
        name="relation_pkey",
    )


class Asset(Base):
    __tablename__ = "asset"

    id = sa.Column(
        sa.UUID(), autoincrement=False, nullable=False, default=generate_uuid
    )
    created_time = sa.Column(
        sa.BIGINT(), autoincrement=False, nullable=False, default=timestamp
    )
    additional_info = sa.Column(sa.VARCHAR(), autoincrement=False, nullable=True)
    type = sa.Column(sa.VARCHAR(length=255), autoincrement=False, nullable=True)
    name = sa.Column(sa.VARCHAR(length=255), autoincrement=False, nullable=False)

    sa.PrimaryKeyConstraint(id)
    sa.UniqueConstraint(name, type)


class Device(Base):
    __tablename__ = "device"

    id = sa.Column(
        sa.UUID(), autoincrement=False, nullable=False, default=generate_uuid
    )
    created_time = sa.Column(
        sa.BIGINT(), autoincrement=False, nullable=False, default=timestamp
    )
    additional_info = sa.Column(sa.VARCHAR(), autoincrement=False, nullable=True)
    type = sa.Column(sa.VARCHAR(length=255), autoincrement=False, nullable=True)
    name = sa.Column(sa.VARCHAR(length=255), autoincrement=False, nullable=False)
    credential = sa.Column(sa.VARCHAR(length=255), autoincrement=False, nullable=False)

    sa.PrimaryKeyConstraint(id)
    sa.UniqueConstraint(credential)


class Attribute(Base):
    __tablename__ = "attribute_kv"
    entity_id = sa.Column(sa.UUID(), autoincrement=False)

    # entity_id = sa.Column(sa.UUID(),  sa.ForeignKey(
    #     Device.id, ondelete='CASCADE'),  autoincrement=False,)
    entity_type = sa.Column(sa.VARCHAR(length=255), autoincrement=False, nullable=True)
    attribute_type = sa.Column(
        sa.VARCHAR(length=255), autoincrement=False, nullable=False
    )
    attribute_key = sa.Column(
        sa.VARCHAR(length=255), autoincrement=False, nullable=False
    )
    value = sa.Column(sa.VARCHAR(length=10000000), autoincrement=False, nullable=True)
    last_update_ts = sa.Column(
        sa.BIGINT(), autoincrement=False, nullable=False, default=timestamp
    )

    sa.PrimaryKeyConstraint(
        entity_id, entity_type, attribute_type, attribute_key, name="attribute_kv_pkey"
    )


class Telemetry(Base):
    __tablename__ = "ts_kv"
    entity_id = sa.Column(sa.UUID(), autoincrement=False)
    key = sa.Column(sa.VARCHAR(length=255), autoincrement=False, nullable=False)
    value = sa.Column(sa.VARCHAR(length=10000000), autoincrement=False, nullable=True)
    ts = sa.Column(sa.BIGINT(), autoincrement=False, nullable=False, default=timestamp)
    sa.PrimaryKeyConstraint(entity_id, key, ts)
