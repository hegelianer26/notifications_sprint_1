import uuid

from sqlalchemy import (Column, String, Text, SmallInteger, MetaData)
from sqlalchemy.dialects.postgresql import UUID

from .database import Base


metadata = MetaData()

class Notification(Base):
    __tablename__ = 'notify_1'

    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, unique=True)
    status = Column(String(16), default='pending')
    retry_count = Column(SmallInteger, default=0)
    device_id = Column(String(255))
    template_id = Column(SmallInteger)
    user_id = Column(String(255))
    group_id = Column(String(255))
    message = Column(Text)


class NotificationDB(Base):
    __tablename__ = 'notify_3'

    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, unique=True)
    status = Column(String(16), default='pending')
    user_groups = Column(String(255))
    sender = Column(String(255))
    subject = Column(String(255))
    content = Column(Text)
