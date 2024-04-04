
from datetime import datetime
from functools import lru_cache

from auth_scheme import CustomScheme
from db.redis import get_redis
from db.sql import models
from db.sql.crud import PostgresCRUD, get_crud_service
from fastapi import APIRouter, Depends, Request, Response
from fastapi.encoders import jsonable_encoder
from redis.asyncio import Redis

router = APIRouter()

oauth2_scheme1 = CustomScheme(tokenUrl="token")


ACCESS_TOKEN_EXPIRE_MINUTES = 4
REFRESH_TOKEN_EXPIRE_MINUTES = 25


class AuthService:
    def __init__(self, crud: PostgresCRUD, redis: Redis):
        self.crud = crud
        self.redis = redis

    async def create_user(self, user):
        return await self.crud.create_user(user=user)

    async def get_user(self, username):
        db_user = await self.crud.get_user_by_email(username)
        return db_user

    async def verify_password(self, db_user, password):
        password_check = db_user.check_password(password)
        return password_check

    async def check_refresh_token(self, user_id, user_agent):
        refresh_token_check = await self.crud.get_refresh_token(
            user_id=user_id, user_agent=user_agent)
        return refresh_token_check

    async def delete_refresh_token(self, refresh_token):
        await self.crud.delete_refresh_token_by_token(refresh_token)

    async def delete_refresh_tokens_by_user(self, user_id):
        await self.crud.delete_refresh_tokens_by_user(user_id)

    async def create_tokens(self, db_user, user_agent):
        data = {}

        token_payload = jsonable_encoder(db_user)
        token_payload["user_agent"] = user_agent
        full_roles = token_payload["roles"]

        roles = [role['name'] for role in full_roles]
        token_payload["roles"] = roles

        access_token = await oauth2_scheme1.create_token(
            token_payload, ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token = await oauth2_scheme1.create_token(
            token_payload, REFRESH_TOKEN_EXPIRE_MINUTES)

        data["data"] = token_payload
        refresh_token_dict = {
            "user_id": db_user.uuid,
            "user_agent": user_agent,
            "refresh_token": refresh_token, }

        user_history_data = {
            "user_id": db_user.uuid,
            "user_agent": user_agent,
            "logged_in_at": datetime.utcnow(),}

        await self.crud.add_data_to_table(
            models.RefreshToken, refresh_token_dict)
        await self.crud.add_data_to_table(
            models.UserSignIn, user_history_data)
        return {"access_token": access_token, "refresh_token": refresh_token}

    async def set_cookies(self, response, access_token, refresh_token):
        response.set_cookie(
            key="refresh_token", httponly=True, value=refresh_token)
        response.set_cookie(
            key="Authorization", httponly=True, value=f"Bearer {access_token}")
        return response

    async def refresh_tokens(self, token_data, user_id, user_agent):

        access_token = await oauth2_scheme1.create_token(
            token_data, ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token = await oauth2_scheme1.create_token(
            token_data, REFRESH_TOKEN_EXPIRE_MINUTES)

        refresh_token_dict = {
            "user_id": user_id,
            "user_agent": user_agent,
            "refresh_token": refresh_token, }

        await self.crud.add_data_to_table(
            models.RefreshToken, refresh_token_dict)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            }

    async def set_deleted_tokens(self, user_id, token):
        await self.redis.setex(
                f'deleted_access_token_for_{user_id}',
                ACCESS_TOKEN_EXPIRE_MINUTES*60,
                token)

@lru_cache()
def get_auth_service(
    crud: PostgresCRUD = Depends(get_crud_service),
    redis: Redis = Depends(get_redis),
) -> AuthService:
    return AuthService(
        crud=crud,
        redis=redis)
