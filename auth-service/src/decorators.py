from functools import wraps
from typing import Callable

from core.config import fastapi_config
from fastapi import HTTPException, status
from jose import JWTError, jwt

SECRET_KEY = fastapi_config.jwt_secret_key
ALGORITHM = fastapi_config.jwt_algorithm


def require_admin_role(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},)

        request = kwargs.get('request') if 'request' in kwargs else args[1]
        try:
            token_dirty = request.cookies.get("Authorization")
            if token_dirty is None or token_dirty == '':
                raise credentials_exception
            token = token_dirty[7:]

            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            user_role: str = payload.get("is_admin")
            token_user_agent: str = payload.get("user_agent")
            user_agent: str = request.headers.get("user-agent")

            if user_role is False or user_agent != token_user_agent:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Operation not permitted"
                )
        except JWTError:
            raise credentials_exception

        return await func(*args, **kwargs)
    return wrapper


def require_authentication(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},)

        request = kwargs.get('request') if 'request' in kwargs else args[1]
        try:
            token_dirty = request.cookies.get("Authorization")
            if token_dirty is None or token_dirty == '':
                raise credentials_exception
            token = token_dirty[7:]

            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            token_user_agent: str = payload.get("user_agent")
            user_agent: str = request.headers.get("user-agent")

            # to do check redis deleted token

            if user_agent != token_user_agent:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Operation not permitted"
                )
        except JWTError:
            raise credentials_exception

        return await func(*args, **kwargs)
    return wrapper
