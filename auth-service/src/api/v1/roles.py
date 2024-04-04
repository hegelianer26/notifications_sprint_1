from auth_scheme import security_jwt
from decorators import require_admin_role
from fastapi import (APIRouter, Depends, HTTPException, Request, Response,
                     status)
from models import entity
from pydantic import UUID4
from services.role_service import RoleService, get_role_service

router = APIRouter()

@router.post("/users/{user_id}/role",
             response_model=entity.UserRoleCreate,
             summary="Назначить роль пользователю",
             description="Назначить роль пользователю",
             response_description="айдишник роли",
             tags=["управление ролями"],
             status_code=status.HTTP_201_CREATED, )
@require_admin_role
async def create_role_for_user(
        user_id: UUID4,
        role: entity.UserRoleCreate,
        request: Request,
        service: RoleService = Depends(get_role_service),
        user: dict = Depends(security_jwt),):
    roles = await service.get_user_role(user_id=user_id, role_id=role.role_id) # from token
    if roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has this role")
    new_role = await service.create_user_role(role_id=role.role_id, user_id=user_id)
    return new_role

@router.post("/",
             response_model=entity.RoleCreate,
             summary="Создать роль",
             description="Добавить роль в базу данных",
             response_description="название роли, описание",
             tags=["управление ролями"],
             status_code=status.HTTP_201_CREATED, )
@require_admin_role
async def create_role(
        role: entity.RoleCreate,
        request: Request,
        service: RoleService = Depends(get_role_service),
        user: dict = Depends(security_jwt),):
    role_ = await service.get_role_by_name(role_name=role.name)
    if role_:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role already eixists")
    new_role = await service.create_role(role=role)
    return new_role

@router.get("/",
            response_model=list[entity.RoleDB],
            summary="Роли",
            description ="Посмотреть все доступные роли",
            response_description="название роли, описание, айдишник",
            tags=["управление ролями"],
            )
@require_admin_role
async def read_roles(
        request: Request,
        skip: int = 0,
        limit: int = 100,
        service: RoleService = Depends(get_role_service),
        user: dict = Depends(security_jwt),):
    roles = await service.get_roles(skip=skip, limit=limit)
    return roles

@router.get("/{user_id}/role/",
            response_model=list[entity.UserRolesInDB],
            summary="Роль пользователя",
            description="Посмотреть роль пользователя",
            response_description="название роли, описание, айдишник",
            tags=["управление ролями"],)
@require_admin_role
async def read_role(user_id: UUID4,
                    request: Request,
                    service: RoleService = Depends(get_role_service),
                    user: dict = Depends(security_jwt),):
    role = await service.get_user_roles(user_id=user_id) # from token
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found")
    return role

@router.delete("/{role_id}",
               summary="Удалить роль",
               description="Удалить роль из базы данных",
               tags=["управление ролями"],
               status_code=status.HTTP_204_NO_CONTENT, )
@require_admin_role
async def delete_role(
        role_id: UUID4,
        request: Request,
        service: RoleService = Depends(get_role_service),
        user: dict = Depends(security_jwt),):
    role = await service.get_role_by_uuid(role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found")
    await service.delete_role(role_id=role_id)
    return

@router.patch("/{role_id}",
              summary="Изменить роль",
              description="Изменить название или описание роли",
              response_description="название роли, описание",
              tags=["управление ролями"],)
@require_admin_role
async def change_role(
        role_id: UUID4,
        request: Request,
        update_data: entity.RoleCreate,
        service: RoleService = Depends(get_role_service),
        user: dict = Depends(security_jwt),):
    updated_role = await service.update_role(
        role_id=role_id, update_data=update_data)
    return updated_role

@router.delete("/{user_id}/role/",
               summary="Удалить роль пользователя",
               description="Удалить роль пользователя из базы данных",
               tags=["управление ролями"],
               status_code=status.HTTP_204_NO_CONTENT, )
@require_admin_role
async def delete_user_role(
        user_id: UUID4,
        response: Response,
        request: Request,
        service: RoleService = Depends(get_role_service),
        user: dict = Depends(security_jwt),):
    user_ = await service.get_user(user_id=user_id)
    if not user_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found")
    await service.delete_user_role(user_id=user_id) # какую то конкретную надо же
    return
