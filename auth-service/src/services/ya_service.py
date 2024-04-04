
import secrets
from functools import lru_cache

import aiohttp
from auth_scheme import CustomScheme
from db.sql.crud import PostgresCRUD, get_crud_service
from fastapi import APIRouter, Depends
from models import entity

router = APIRouter()

oauth2_scheme1 = CustomScheme(tokenUrl="token")


ACCESS_TOKEN_EXPIRE_MINUTES = 4
REFRESH_TOKEN_EXPIRE_MINUTES = 25


class OauthService:
    def __init__(self, crud: PostgresCRUD):
        self.crud = crud

    async def get_user_info(self, login_url: str, access_token: str):
        session = aiohttp.ClientSession()
        async with session.post(url=login_url,
                                headers={"Authorization": f'OAuth {access_token}',
                                        'format': 'json | xml | jwt'},) as resp:
            user_info = await resp.json()
        await session.close()
        return user_info

    async def get_social_account(self, social_id: str, social_name: str):
        social_account = await self.crud.get_social_account(
            social_id=social_id, social_name=social_name)
        return social_account

    async def get_user_by_id(self, user_id: str):
        db_user = await self.crud.get_user(user_id)
        return db_user

    async def get_user_by_email(self, username: str):
        db_user = await self.crud.get_user_by_email(username)
        return db_user

    async def create_user(self, username: str):
        password = secrets.token_urlsafe(16)
        user_for_db = entity.UserCreate(
                username=username, password=password)
        user = await self.crud.create_user(user=user_for_db)
        return user

    async def create_social_account(
                self, user_id: str, social_id: str, social_name: str):
        social_account = entity.SocialAccCreate(
            social_id=social_id, social_name=social_name, user_id=user_id)
        await self.crud.create_social_account(social_account)


@lru_cache()
def get_oauth_service(
    crud: PostgresCRUD = Depends(get_crud_service),
) -> OauthService:
    return OauthService(
        crud=crud)
