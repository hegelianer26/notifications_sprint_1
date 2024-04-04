import uuid
from datetime import datetime

from passlib.context import CryptContext
from sqlalchemy import (TIMESTAMP, Boolean, Column, DateTime, ForeignKey,
                        String, Text, UniqueConstraint, event, or_, text)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pydantic import EmailStr

from .database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_partition(target, connection, **kw) -> None:
    """creating partition by user_sign_in"""
    connection.execute(
        text(
            """CREATE TABLE IF NOT EXISTS "users_sign_in_2024_1" PARTITION OF "users_sign_in" FOR VALUES FROM ('2024-01-01') TO ('2024-07-01');"""
        )
    )
    connection.execute(
        text(
            """CREATE TABLE IF NOT EXISTS "users_sign_in_2024_2" PARTITION OF "users_sign_in" FOR VALUES FROM ('2024-07-01') TO ('2024-12-31');"""
        )
    )


class User(Base):
    __tablename__ = "users"

    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, unique=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, nullable=False) 
    password = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) # todo! важно, чтобы нормально создать базу рассылки

    roles = relationship('Role', secondary='user_roles', back_populates='users')

    groups = relationship('Group', secondary='user_groups', back_populates='users')


    def __init__(self, username: str, password: str, email: EmailStr) -> None:
        self.username = username
        self.email = email
        self.password = pwd_context.hash(password)
        self.groups.append(Group(name='basic')) 

    def check_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password)

    @classmethod
    def get_user_by_universal_login(cls, username: str | None = None, email: str | None = None):
        return cls.query.filter(or_(
            cls.username == username, cls.email == email)).first()

    def __repr__(self) -> str:
        return f'<User {self.username}>' 


class Role(Base):
    __tablename__ = "roles"

    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, unique=True)
    name = Column(String(50), index=True, unique=True)
    description = Column(String(500), index=True)

    users = relationship('User', secondary='user_roles', back_populates='roles')


class UserRole(Base):
    __tablename__ = "user_roles"

    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, unique=True)
    user_id = Column(UUID, ForeignKey("users.uuid", ondelete='CASCADE'), nullable=False)
    role_id = Column(UUID, ForeignKey("roles.uuid", ondelete='CASCADE'), nullable=False)

    __table_args__ = (UniqueConstraint('user_id', 'role_id', name='_user_role_uc'),)


class Group(Base):
    __tablename__ = 'groups'

    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, unique=True)
    name = Column(String, default='basic')
    # description = Column(String(500), index=True) # todo

    users = relationship('User', secondary='user_groups', back_populates='groups')


class UserGropus(Base):
    __tablename__ = "user_groups"

    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, unique=True)
    user_id = Column(UUID, ForeignKey("users.uuid", ondelete='CASCADE'), nullable=False)
    group_id = Column(UUID, ForeignKey("groups.uuid", ondelete='CASCADE'), nullable=False)

    __table_args__ = (UniqueConstraint('user_id', 'group_id', name='_user_group_uc'),)


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, unique=True)
    user_id = Column(UUID, ForeignKey("users.uuid", ondelete="CASCADE"))
    refresh_token = Column(String, nullable=False)
    date_created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    user_agent = Column(Text, nullable=False)

    user = relationship("User")

    __table_args__ = (UniqueConstraint('user_id', 'user_agent', name='_user_agent_uc'),)


class UserSignIn(Base):
    __tablename__ = 'users_sign_in'
    __table_args__ = (UniqueConstraint('uuid', 'logged_in_at', 'user_agent'),

        {
            'postgresql_partition_by': 'RANGE (logged_in_at)',
            'listeners': [('after_create', create_partition)],
        }
    )
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    user_id = Column(UUID, ForeignKey("users.uuid", ondelete='CASCADE'))
    logged_in_at = Column(DateTime, default=datetime.utcnow, primary_key=True)
    user_agent = Column(String)


    def __repr__(self):
        return f'<UserSignIn {self.user_id}:{self.logged_in_at }>'


class SocialAccount(Base):
    __tablename__ = 'social_account'

    uuid = Column(UUID(as_uuid=True),  default=uuid.uuid4, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.uuid'), nullable=False)
    user = relationship(User, backref='social_accounts', lazy=True)

    social_id = Column(Text, nullable=False)
    social_name = Column(Text, nullable=False)

    __table_args__ = (UniqueConstraint('social_id', 'social_name', name='social_pk'), )

    def __repr__(self):
        return f'<SocialAccount {self.social_name}:{self.user_id}>'
