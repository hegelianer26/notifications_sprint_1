from auth_scheme import CustomScheme, security_jwt
from decorators import require_admin_role, require_authentication
from fastapi import APIRouter, Depends, HTTPException, Request
from models import entity
from pydantic import UUID4
from services.user_service import UserService, get_user_service

oauth2_scheme1 = CustomScheme(tokenUrl="token")
router = APIRouter()

from core.config import external_auth

@router.get("/me/",
            response_model=entity.UserMe,
            summary="Личная информация",
            description="Информация об активном пользователей",
            response_description="айди, логин, имя и фамилия",
            tags=["управление пользователями"],)
async def read_users_me(request: Request,
                        service: UserService = Depends(get_user_service),
                        user: dict = Depends(security_jwt),):
    current_user = await service.get_me(username=user.get("username"))
    return current_user

@router.patch("/me/",
              summary="Обновить личную информацию",
              description="Обновить информацию активного пользователя",
              response_description="Обновлённая информация пользователя",
              tags=["управление пользователями"])
async def update_user_me(request: Request,
                         update_data: entity.UserUpdate,
                         service: UserService = Depends(get_user_service),
                         user: dict = Depends(security_jwt)):
    updated_user = await service.update_user_me(
        user_id=user.get('uuid'), update_data=update_data)
    return updated_user

@router.get("/me/history/",
            response_model=list[entity.UserHistory],
            summary="История входов в аккаунт",
            description="История входов с разных устройств и т.п.",
            response_description="устройство, дата и время",
            tags=["управление пользователями"],)
async def read_user_history(request: Request,
                            skip: int = 0,
                            limit: int = 100,
                            service: UserService = Depends(get_user_service),
                            user: dict = Depends(security_jwt),):
    history = await service.get_user_history(user_id=user.get('uuid'), skip=skip, limit=limit)
    return history

@router.get("/",
            response_model=list[entity.UsersInDB],
            summary="Список пользователей",
            description="Посмотреть всех пользователей в базе данных",
            response_description="айдишник, логин, имя и фамилия",
            tags=["управление пользователями"],)
async def read_users(request: Request,
                     skip: int = 0,
                     limit: int = 100,
                     service: UserService = Depends(get_user_service),
                     ):
    users = await service.get_users(skip=skip, limit=limit)
    return users

@router.get("/{user_id}",
            response_model=entity.FullUserInDB,
            summary="Информация о пользвателе", 
            description="Посмотреть всю информацию о пользователе в базе данных",
            response_description="айдишник, логин, имя и фамилия",
            tags=["управление пользователями"],)
@require_admin_role
async def read_user(user_id: UUID4,
                    request: Request,
                    service: UserService = Depends(get_user_service),
                    user: dict = Depends(security_jwt),):
    db_user = await service.get_user(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
