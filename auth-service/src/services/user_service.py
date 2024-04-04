from functools import lru_cache

from db.sql.crud import PostgresCRUD, get_crud_service
from fastapi import Depends
from models import entity
from pydantic import UUID4


class UserService:
    def __init__(self, crud: PostgresCRUD):
        self.crud = crud

    async def get_me(self, username: str):
        current_user = await self.crud.get_user_by_email(username)
        return current_user

    async def update_user_me(self, user_id: UUID4,
                             update_data: entity.UserUpdate,):
        updated_user = await self.crud.update_user(user_id, update_data)
        return updated_user

    async def get_user_history(self,
                               user_id: UUID4,
                               skip: int = 0,
                               limit: int = 100,):
        history = await self.crud.get_user_history(user_id, skip=skip, limit=limit)
        return history

    async def get_users(self,
                        skip: int = 0,
                        limit: int = 100,):
        users = await self.crud.get_users(skip=skip, limit=limit)
        return users

    async def get_user(self, user_id: UUID4):
        db_user = await self.crud.get_user(user_id)
        return db_user

@lru_cache()
def get_user_service(
    crud: PostgresCRUD = Depends(get_crud_service),
) -> UserService:
    return UserService(
        crud=crud)
