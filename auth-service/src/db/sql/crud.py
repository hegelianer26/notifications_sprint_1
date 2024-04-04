from functools import lru_cache

from db.sql import models
from db.sql.database import get_session
from fastapi import Depends
from models import entity
from passlib.context import CryptContext
from pydantic import UUID4
from sqlalchemy import and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload


class PostgresCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, user_id: int):
        result = await self.session.execute(
            select(models.User).where(models.User.uuid == user_id).options(joinedload(models.User.roles)))
        return result.scalars().first()

    async def get_user_by_email(self, username: str):
        result = await self.session.execute(
            select(models.User).where(models.User.username == username).options(joinedload(models.User.roles)))
        return result.scalar()

    async def get_users(self, skip: int = 0, limit: int = 100):
        result = await self.session.execute(select(models.User).offset(skip).limit(limit))
        return result.scalars().all()

    async def create_user(self, user: entity.UserCreate):
        db_user = models.User(**user.model_dump())
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def get_social_account(
            self, social_id: str, social_name: str):
        result = await self.session.execute(
                select(models.SocialAccount).where(
                    and_(
                        models.SocialAccount.social_id == social_id,
                        models.SocialAccount.social_name == social_name)))
        return result.scalars().first()

    async def create_social_account(
            self, social_account: entity.SocialAccCreate):
        db_user = models.SocialAccount(**social_account.model_dump())
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def create_role(self, role: entity.RoleCreate):
        db_role = models.Role(**role.model_dump())
        self.session.add(db_role)
        await self.session.commit()
        await self.session.refresh(db_role)
        return db_role

    async def create_group(self, group: entity.GroupCreate):
        db_group = models.Group(**group.model_dump())
        self.session.add(db_group)
        await self.session.commit()
        await self.session.refresh(db_group)
        return db_group

    def create_role1(self, name, description):
        db_role = models.Role(name=name, description=description)
        self.session.add(db_role)
        self.session.commit()
        self.session.refresh(db_role)
        return db_role

    async def get_roles(self, skip: int = 0, limit: int = 100):
        result = await self.session.execute(select(models.Role).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_role(self, role_id: UUID4):
        result = await self.session.execute(select(models.Role).where(models.Role.uuid == role_id))
        return result.scalars().first()

    async def get_role_by_name(self, role_name: UUID4):
        result = await self.session.execute(select(models.Role).where(models.Role.name == role_name))
        return result.scalars().first()
    
    async def get_group_by_name(self, group_name: UUID4):
        result = await self.session.execute(select(models.Role).where(models.Group.name == group_name))
        return result.scalars().first()

    async def delete_role(self, role_id: UUID4):
        db_role = await self.session.execute(select(models.Role).where(models.Role.uuid == role_id))
        role_to_delete = db_role.scalars().first()
        await self.session.delete(role_to_delete)
        await self.session.commit()
        return db_role

    async def get_refresh_token(self, user_id: UUID4, user_agent: str):
        result = await self.session.execute(
                select(models.RefreshToken).where(
                    and_(
                        models.RefreshToken.user_id == user_id,
                        models.RefreshToken.user_agent == user_agent)))
        return result.scalars().first()

    async def delete_refresh_token(self, user_id: UUID4):
        db_refresh_token = await self.session.execute(
            select(models.RefreshToken).where(
                models.RefreshToken.user_id == user_id))
        refresh_token_to_delete = db_refresh_token.scalars().first()
        await self.session.delete(refresh_token_to_delete)
        await self.session.commit()
        return db_refresh_token

    async def delete_refresh_token_by_token(self, db_refresh_token: str):
        db_refresh_token = await self.session.execute(
            select(models.RefreshToken).where(
                models.RefreshToken.refresh_token == db_refresh_token))
        refresh_token_to_delete = db_refresh_token.scalars().first()
        await self.session.delete(refresh_token_to_delete)
        await self.session.commit()
        return db_refresh_token

    async def delete_refresh_tokens_by_user(self, user_id: UUID4):
        db_refresh_tokens = await self.session.execute(
            select(models.RefreshToken).where(
                models.RefreshToken.user_id == user_id))
        refresh_tokens_to_delete = db_refresh_tokens.scalars().all()
        for token in refresh_tokens_to_delete:
            await self.session.delete(token)
        await self.session.commit()

    async def add_data_to_table(self, model, data: list):
        adding_data = model(**data)
        self.session.add(adding_data)
        await self.session.commit()
        await self.session.refresh(adding_data)

    async def get_user_history(self, user_id: UUID4, skip: int = 0, limit: int = 100):
        result = await self.session.execute(
            select(models.UserSignIn).where(
                models.UserSignIn.user_id == user_id).offset(skip).limit(limit))
        return result.scalars().all()

    async def update_user(self, user_id: UUID4, update_data):
        new_data = update_data.model_dump()
        if new_data['password']:
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            new_data['password'] = pwd_context.hash(new_data['password'])

        result = await self.session.execute(
            update(models.User).where(
                models.User.uuid == user_id).values(**new_data))
        await self.session.commit()
        return result

    async def update_role(self, role_id: UUID4, update_data):
        new_data = update_data.model_dump(exclude_unset=True)
        result = await self.session.execute(
            update(models.Role).where(
                models.Role.uuid == role_id).values(**new_data))
        await self.session.commit()
        return result

    async def create_user_role(self, user_id: UUID4, role_id: UUID4):
        db_role = models.UserRole(user_id=user_id, role_id=role_id)
        self.session.add(db_role)
        await self.session.commit()
        await self.session.refresh(db_role)
        return db_role

    async def create_user_group(self, user_id: UUID4, group_id: UUID4):
        db_group = models.UserGropus(user_id=user_id, group_id=group_id)
        self.session.add(db_group)
        await self.session.commit()
        await self.session.refresh(db_group)
        return db_group

    async def delete_user_role(self, user_id: UUID4):
        db_user_role = await self.session.execute(
            select(models.UserRole).where(models.UserRole.user_id == user_id))
        user_role_to_delete = db_user_role.scalars().first()
        await self.session.delete(user_role_to_delete)
        await self.session.commit()
        return db_user_role

    async def delete_user_group(self, user_id: UUID4, group_id: UUID4):
        db_user_group = await self.session.execute(
            select(models.UserGropus).where(
                and_(models.UserGropus.user_id == user_id, models.UserGropus.group_id == group_id)))
        user_group_to_delete = db_user_group.scalars().first()
        await self.session.delete(user_group_to_delete)
        await self.session.commit()
        return user_group_to_delete

    async def get_user_role(self, user_id: UUID4, role_id: UUID4):
        result = await self.session.execute(
            select(models.UserRole).where(
                and_(models.UserRole.user_id == user_id, models.UserRole.role_id == role_id)))
        return result.scalars().first()

    async def get_user_group(self, user_id: UUID4, group_id: UUID4):
        result = await self.session.execute(
            select(models.UserGropus).where(
                and_(models.UserGropus.user_id == user_id, models.UserGropus.group_id == group_id)))
        return result.scalars().first()

    async def get_user_roles(self, user_id: UUID4):
        result2 = await self.session.execute(
            select(models.User).where(models.User.uuid == user_id).options(
                selectinload(models.User.roles)))
        return result2.scalars().all()

@lru_cache()
def get_crud_service(
    session: AsyncSession = Depends(get_session),
) -> PostgresCRUD:
    return PostgresCRUD(session)
