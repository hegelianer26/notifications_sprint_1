import time
from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import aiohttp
from core.config import fastapi_config
from fastapi import HTTPException, Request, Response, status
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from models import entity
from passlib.context import CryptContext
from pydantic import UUID4
from redis.asyncio import Redis

SECRET_KEY = fastapi_config.jwt_secret_key
ALGORITHM = fastapi_config.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 1
REFRESH_TOKEN_EXPIRE_MINUTES = 25

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CustomScheme(OAuth2PasswordBearer):

    async def verify_token(self, token: str):
        credential_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}        
        )

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        except JWTError:
            raise credential_exception
        return payload

    async def create_token(self, data: dict, expires_delta: int | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(tz=timezone.utc) + timedelta(minutes=expires_delta)
        else:
            expire = datetime.now(tz=timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def get_current_user_info(self, request: Request):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        signature_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
        token = await self._get_token(request)
        try:
            payload = await self._get_token_data(
                token, SECRET_KEY, algorithms=[ALGORITHM])
        except ExpiredSignatureError:
            raise signature_exception

        try:
            username: str = payload.get("username")
            user_agent: str = payload.get("user_agent")
            uuid: UUID4 = payload.get("uuid")
            if username is None:
                raise credentials_exception
            if user_agent != request.headers.get("user-agent"):
                raise credentials_exception
            token_data = entity.TokenData(username=username, uuid=uuid)
        except JWTError:
            raise credentials_exception
        # user = await crud.get_user_by_email(db, username=token_data.username)
        if token_data.username is None:
            raise credentials_exception
        return token_data

    async def _get_token(self, request: Request):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            token_dirty = request.cookies.get("Authorization")
            if token_dirty is None or token_dirty == '':
                raise credentials_exception
            token = token_dirty[7:]
        except JWTError:
            raise credentials_exception

        return token

    async def _get_token_data(self, token: str, secret_key: str, algorithms: list[str]):
        payload = jwt.decode(token, secret_key, algorithms)
        return payload

    async def _get_token_data_without_expire(self, token: str):

        token_data = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False},)
        return token_data

    async def check_tokens_exp(self, request: Request):

        current_token = await self._get_token(request)
        current_token_data = await self._get_token_data_without_expire(current_token)
        expire = current_token_data.get("exp")

        if int(time.time()) > expire:
            return True
        return False

    async def get_token_from_redis(self, user_agent: str, user_id: UUID4, redis: Redis):

        deleted_token = await redis.get(
            'deleted_access_token_for_{user_id}_{user_agent}')

        if not deleted_token:
            return None

        return deleted_token


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request, response: Response) -> dict:

        token_dirty = request.cookies.get("Authorization")

        if not token_dirty or token_dirty == '':
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail='Invalid authorization code.')
        if not token_dirty[:6] == 'Bearer':
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail='Only Bearer token might be accepted')
        decoded_token = self.parse_token(token_dirty[7:])
        token_user_agent: str = decoded_token.get("user_agent")
        user_agent: str = request.headers.get("user-agent")

        if not decoded_token or user_agent != token_user_agent:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail='Invalid token.')
        expire = decoded_token.get("exp")
        if int(time.time()) < expire:
            return decoded_token

        session = aiohttp.ClientSession()
        url = f'http://{fastapi_config.auth_host}:{fastapi_config.auth_port}/auth/api/v1/auth/refresh'
        print('asdas', url)
        cookies = {'Authorization': request.cookies.get('Authorization'),
                   'refresh_token': request.cookies.get('refresh_token')}
        headers = {'user-agent': request.headers.get('user-agent')}

        async with session.get(url, cookies=cookies, headers=headers) as resp:
            status = resp.status
            body = await resp.json()
            new_token = body.get('access_token')
            new_refresh_token = body.get('refresh_token')

        await session.close()

        if status != HTTPStatus.OK:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail='Tokens are expired.')

        response.set_cookie(
            key="refresh_token", httponly=True, value=new_refresh_token)
        response.set_cookie(
            key="Authorization", httponly=True, value=f"Bearer {new_token}")
        decoded_token = self.parse_token(new_token) # взять из ретурна сессии

        return decoded_token

    @staticmethod
    def parse_token(jwt_token: str):
        return jwt.decode(
            jwt_token, SECRET_KEY, algorithms=ALGORITHM, options={
                "verify_exp": False},)


security_jwt = JWTBearer()
