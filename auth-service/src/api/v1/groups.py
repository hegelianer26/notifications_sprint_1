from auth_scheme import security_jwt
from decorators import require_admin_role
from fastapi import (APIRouter, Depends, HTTPException, Request, Response,
                     status)
from models import entity
from pydantic import UUID4
from services.group_service import GroupService, get_group_service

router = APIRouter()


@router.post("/",
             response_model=entity.GroupCreate,
             summary="Создать группу",
             description="Грыппы используются для рассылки уведомлений",
             response_description="название группы, описание",
             tags=["управление группами рассылки"],
             status_code=status.HTTP_201_CREATED, )
@require_admin_role
async def create_role(
        role: entity.GroupCreate,
        request: Request,
        service: GroupService = Depends(get_group_service),
        user: dict = Depends(security_jwt),):
    group_ = await service.get_group_by_name(role_name=role.name)
    if group_:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group already eixists")
    new_group = await service.create_group(role=role)
    return new_group


@router.post("/gropus/{user_id}/role",
             response_model=entity.UserGroupCreate,
             summary="Назначить группу пользователю",
             description="Назначить группу для рассылки для пользователя",
             response_description="айдишник группы",
             tags=["управление группами рассылки"],
             status_code=status.HTTP_201_CREATED, )
async def create_role_for_user(
        user_id: UUID4,
        group: entity.UserGroupCreate,
        request: Request,
        service: GroupService = Depends(get_group_service),
        user: dict = Depends(security_jwt),):
    groups = await service.get_user_role(
        user_id=user_id, group_id=group.group_id) # from token
    if groups:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has this role")
    new_group = await service.create_user_group(
        group_id=group.role_id, user_id=user_id)
    return new_group


@router.delete("/gropus/{user_id}/role",
             summary="отписаться от рассылки",
             description="отписаться от групп рассылки",
             tags=["управление группами рассылки"],
             status_code=status.HTTP_204_NO_CONTENT, )
async def delete_group(
        group_id: UUID4,
        request: Request,
        service: GroupService = Depends(get_group_service),
        user: dict = Depends(security_jwt),):
    groups = await service.get_user_role(
        user_id=user.uuid, group_id=group_id) 
    if not groups:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found")
    await service.delete_user_group(group_id=group_id, user_id=user.uuid)
    return
