from functools import lru_cache

from db.postgres import models
from db.postgres.database import get_session
from fastapi import Depends
from models.entity import Notification, EmailCampaign
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession


class PostgresCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def post_notifications_in_db(self, body: list[Notification]):
        notifications = [models.Notification(**notification.model_dump()) for notification in body]
        self.session.add_all(notifications)
        await self.session.commit()
        return notifications

    async def post_notifications_db(self, body: list[EmailCampaign]):
        notifications = [models.NotificationDB(**notification.model_dump()) for notification in body]
        self.session.add_all(notifications)
        await self.session.commit()
        return notifications
    

@lru_cache()
def get_crud_service(
    session: AsyncSession = Depends(get_session),
) -> PostgresCRUD:
    return PostgresCRUD(session)
