import uuid
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID

from db import Base


class NotificationDB(Base):
    __tablename__ = 'notify_history'

    notification_uuid = Column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, unique=True)
    campaign_uuid = Column(String(255))
    status = Column(String(16), default='pending')
    user_groups = Column(String(255))
    sender = Column(String(255))
    subject = Column(String(255))
    content = Column(Text)
    first_name = Column(String(255))
    last_name = Column(String(255))
    recipient = Column(String(255))
