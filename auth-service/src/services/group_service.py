from functools import lru_cache

from db.sql.crud import PostgresCRUD, get_crud_service
from fastapi import Depends
from models import entity
from pydantic import UUID4


class GroupService:
    def __init__(self, crud: PostgresCRUD):
        self.crud = crud

    async def get_user_group(self, user_id: UUID4, group_id: UUID4):
        groups = await self.crud.get_user_group(user_id, group_id)
        return groups

    async def create_user_group(
            self, user_id: UUID4, group_id: UUID4):
        roles = await self.crud.create_user_group(group_id=group_id, user_id=user_id)
        return roles

    async def get_group_by_name(self, group_name: str):
        group = await self.crud.get_group_by_name(group_name)
        return group

    async def create_group(self, group: entity.GroupCreate):
        group = await self.crud.create_group(group)
        return group

    async def delete_user_group(self, user_id: UUID4, group_id: UUID4):
        await self.crud.delete_user_group(user_id, group_id)


@lru_cache()
def get_group_service(
    crud: PostgresCRUD = Depends(get_crud_service),
) -> GroupService:
    return GroupService(
        crud=crud)
