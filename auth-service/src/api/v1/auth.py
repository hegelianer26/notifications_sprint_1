from auth_scheme import CustomScheme
from db.redis import get_redis
from decorators import require_authentication
from fastapi import (APIRouter, Depends, HTTPException, Request, Response,
                     status)
from fastapi.security import OAuth2PasswordRequestForm
from models import entity
from redis.asyncio import Redis
from services.auth_service import AuthService, get_auth_service
from services.rabbit_service import RabbitService, get_rabbit_service
router = APIRouter()

oauth2_scheme1 = CustomScheme(tokenUrl="token")

@router.post("/login/",
             response_model=entity.UserInDB,
             summary="Регистрация пользователя",
             description="Добавить пользователя в базу данных",
             response_description="айдишник, логин, имя и фамилия",
             tags=["управление пользователями"],
             status_code=status.HTTP_201_CREATED,)
async def create_user(
        user: entity.UserCreate,
        service: AuthService = Depends(get_auth_service),
        rabbit: RabbitService = Depends(get_rabbit_service),):
    db_user = await service.get_user(username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered")
    await rabbit.send_to_queue(user.dict())
    return await service.create_user(user=user)


@router.post("/token/",
             summary="Войти в акканут",
             tags=["управление пользователями"],
             status_code = status.HTTP_200_OK,)
async def login(response: Response,
                request: Request,
                user_login: OAuth2PasswordRequestForm = Depends(),
                service: AuthService = Depends(get_auth_service),):

    db_user = await service.get_user(
        username=user_login.username)

    if not db_user:
        raise HTTPException(detail="Incorrect User email/password",
                            status_code=status.HTTP_409_CONFLICT)

    password_check = await service.verify_password(
        db_user=db_user, password=user_login.password)

    if not password_check:
        raise HTTPException(detail="Incorrect User email/password",
                            status_code=status.HTTP_409_CONFLICT)

    user_id = db_user.uuid
    user_agent = request.headers.get("user-agent")

    refresh_token_check = await service.check_refresh_token(
        user_id=user_id, user_agent=user_agent)

    if refresh_token_check:
        await service.delete_refresh_token(
            refresh_token_check.refresh_token)

    tokens = await service.create_tokens(
        db_user=db_user, user_agent=user_agent)

    response.set_cookie(
            key="refresh_token", httponly=True, value=tokens["refresh_token"])
    response.set_cookie(
            key="Authorization", httponly=True, value=f"Bearer {tokens['access_token']}")

    return {"message": "Successfully logged in",
            "username": db_user.username,
            "first_name": db_user.first_name,
            "last_name": db_user.last_name,
            "is_admin": db_user.is_admin,
            "is_active": db_user.is_active,
            "uuid": db_user.uuid}


@router.get("/refresh", status_code=status.HTTP_200_OK)
async def get_new_tokens(request: Request,
                         response: Response,
                         service: AuthService = Depends(get_auth_service),):

    refresh_token_in_cookies = request.cookies.get("refresh_token")

    token_data = await oauth2_scheme1.verify_token(
        refresh_token_in_cookies)
    user_id = token_data.get("uuid")
    user_agent = request.headers.get("user-agent")

    refresh_token_in_db = await service.check_refresh_token(
        user_id=user_id, user_agent=user_agent)

    if await oauth2_scheme1.check_tokens_exp(request):
# and (
#             refresh_token_in_db.refresh_token == refresh_token_in_cookies)
        if refresh_token_in_db: 
            await service.delete_refresh_token(
                refresh_token_in_db.refresh_token)
        tokens = await service.refresh_tokens(
            token_data, user_id, user_agent)

        response.set_cookie(
                key="refresh_token", httponly=True, value=tokens["refresh_token"])
        response.set_cookie(
                key="Authorization", httponly=True, value=f"Bearer {tokens['access_token']}")

        return {
            "access_token": tokens["access_token"],
            "token_type": "Bearer",
            "refresh_token": tokens["refresh_token"],
            "message": "User Logged in Successfully.",
            "data": token_data,
            "status": status.HTTP_200_OK}

    return {"message": "token is actual"}


@router.post("/logout",
             summary="Выйти из системы",
             tags=["управление пользователями"],
             status_code=status.HTTP_200_OK, )
@require_authentication
async def logout(response: Response,
                 request: Request,
                 service: AuthService = Depends(get_auth_service),):

    old_refresh_token = request.cookies.get("refresh_token")
    token = await oauth2_scheme1._get_token(request)
    token_data = await oauth2_scheme1.verify_token(token)
    user_id = token_data.get("uuid")
    if old_refresh_token:
        await service.delete_refresh_token(old_refresh_token)

    if token:
        await service.set_deleted_tokens(user_id, token)

    response.set_cookie(key="refresh_token", value='')
    response.set_cookie(key="Authorization", value='')

    return {"message": "Successfully logged out"}


@router.post("/logout/all",
          summary="Выйти из всех устройств",
          description="Выйти из всех устройств, где вы залоглонились",
          tags=["управление пользователями"])
@require_authentication
async def logout(response: Response,
                 request: Request,
                 redis: Redis = Depends(get_redis),
                 service: AuthService = Depends(get_auth_service),):

    old_refresh_token = request.cookies.get("refresh_token")
    old_access_token = request.cookies.get("access_token")
    user_agent = request.headers.get("user-agent")

    token = await oauth2_scheme1._get_token(request)
    token_data = await oauth2_scheme1.verify_token(token)
    user_id = token_data.get("uuid")

    if old_refresh_token:
        await service.delete_refresh_tokens_by_user(user_id)

    if old_access_token:
        await service.set_deleted_tokens(user_id, token)

    response.set_cookie(key="refresh_token", value='')
    response.set_cookie(key="Authorization", value='')

    return {"message": "Successfully logged out from everywhere"}
