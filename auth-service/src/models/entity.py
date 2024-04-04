from datetime import datetime

from pydantic import UUID4, BaseModel, EmailStr


class UserRole(BaseModel):
    name: str
    description: str | None = None
    uuid: UUID4
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class SocialAccCreate(BaseModel):
    user_id: UUID4
    social_id: str
    social_name: str


class UserRolesInDB(BaseModel):
    roles: list[UserRole]

    class Config:
        orm_mode = True


class UserInDB(BaseModel):
    uuid: UUID4
    username: str
    email: EmailStr


class UsersInDB(BaseModel):
    uuid: UUID4
    username: str
    first_name: str | None = None
    last_name: str | None = None


class FullUserInDB(BaseModel):
    uuid: UUID4
    username: str
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool
    is_admin: bool
    created_at: datetime
    roles: list[UserRole]


class UserUpdate(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str


class UserMe(BaseModel):
    username: str
    first_name: str | None = None
    last_name: str | None = None


class RoleCreate(BaseModel):
    name: str
    description: str | None = None

    class Config:
        orm_mode = True


class GroupCreate(BaseModel):
    name: str
    description: str | None = None

    class Config:
        orm_mode = True


class RoleDB(RoleCreate):
    uuid: UUID4

    class Config:
        orm_mode = True


class UserRoleCreate(BaseModel):
    role_id: UUID4


class UserGroupCreate(BaseModel):
    group_id: UUID4


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
    uuid: UUID4


class RefreshToken(BaseModel):
    id: str    
    user_id: str
    refresh_token: str
    date_created: str


class UserHistory(BaseModel):
    logged_in_at: datetime
    user_agent: str


class All_TokenData(TokenData):
    password: str
    last_name: str | None = None
    created_at: datetime
    first_name: str
    is_active: bool
    roles: list
