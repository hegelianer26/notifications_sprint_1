from functools import lru_cache

from db.sql.crud import PostgresCRUD, get_crud_service
from fastapi import Depends
from models import entity
from pydantic import UUID4


class RoleService:
    def __init__(self, crud: PostgresCRUD):
        self.crud = crud

    async def get_user_role(self, user_id: UUID4, role_id: UUID4):
        roles = await self.crud.get_user_role(user_id, role_id)
        return roles
    
    async def get_user_group(self, user_id: UUID4, group_id: UUID4):
        groups = await self.crud.get_user_group(user_id, group_id)
        return groups

    async def get_user_roles(self, user_id: UUID4):
        roles = await self.crud.get_user_roles(user_id)
        return roles

    async def create_user_role(
            self, user_id: UUID4, role_id: UUID4):
        roles = await self.crud.create_user_role(role_id=role_id, user_id=user_id)
        return roles
    
    async def create_user_group(
            self, user_id: UUID4, group_id: UUID4):
        roles = await self.crud.create_user_group(group_id=group_id, user_id=user_id)
        return roles

    async def get_role_by_name(self, role_name: str):
        role = await self.crud.get_role_by_name(role_name)
        return role

    async def get_role_by_uuid(self, role_id: UUID4):
        role = self.crud.get_role(role_id)
        return role

    async def create_role(self, role: entity.RoleCreate):
        role = await self.crud.create_role(role)
        return role
    
    async def get_group_by_name(self, group_name: str):
        group = await self.crud.get_group_by_name(group_name)
        return group

    async def create_group(self, group: entity.GroupCreate):
        group = await self.crud.create_group(group)
        return group

    async def update_role(self, role_id: UUID4, update_data):
        result = await self.crud.update_role(role_id, update_data)
        return result

    async def delete_role(self, role_id: UUID4):
        await self.crud.delete_role(role_id)

    async def get_roles(self, skip: int = 0, limit: int = 100):
        roles = await self.crud.get_roles(skip, limit)
        return roles

    async def delete_user_role(self, user_id: UUID4):
        await self.crud.delete_user_role(user_id)

    async def get_user(self, user_id: UUID4):
        user = await self.crud.get_user(user_id)
        return user

    async def delete_user_group(self, user_id: UUID4, group_id: UUID4):
        await self.crud.delete_user_group(user_id, group_id)


@lru_cache()
def get_role_service(
    crud: PostgresCRUD = Depends(get_crud_service),
) -> RoleService:
    return RoleService(
        crud=crud)
