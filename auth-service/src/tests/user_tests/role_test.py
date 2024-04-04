from http import HTTPStatus

import pytest
from core.config import fastapi_config
from db.sql.models import User
from httpx import AsyncClient
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio

SECRET_KEY = fastapi_config.jwt_secret_key
ALGORITHM = fastapi_config.jwt_algorithm

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

new_role = {'name': 'the knight', 'description': 'warrior on horse'}
put_role = {'name': 'The knight', 'description': 'The warrior on white horse'}
role_id_for_user = {'role_id': '26acca1f-80eb-4cc4-a0de-2a160534f211'}

token_in = f"grant_type=&username=admin&password=admin&client_id=&client_secret="
token_in_not_admin = f"grant_type=&username=notadmin&password=notadmin&client_id=&client_secret="

url_token = f'/api/v1/auth/token/'
roles = f'/api/v1/roles/'
user_role = f'/api/v1/roles/users'


async def test_create_role(
    create_admin, client: AsyncClient, session: AsyncSession):

    await client.post(
        url_token,
        headers={'Content-Type': 'application/x-www-form-urlencoded', 'accept': 'application/json'},
        data=token_in)

    response = await client.post(
        roles,
        json=new_role)
    assert response.status_code == HTTPStatus.CREATED


async def test_create_role_only_admin(
    create_not_admin, client: AsyncClient, session: AsyncSession):

    await client.post(
        url_token,
        headers={'Content-Type': 'application/x-www-form-urlencoded', 'accept': 'application/json'},
        data=token_in_not_admin)

    response = await client.post(
        roles,
        json=new_role)
    assert response.status_code == HTTPStatus.FORBIDDEN


async def test_create_role_for_user(
    create_admin, create_not_admin, create_role, client: AsyncClient, session: AsyncSession):

    login = await client.post(
        url_token,
        headers={'Content-Type': 'application/x-www-form-urlencoded', 'accept': 'application/json'},
        data=token_in)

    token = login.cookies.get('refresh_token')
    playload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    user_id = playload['uuid']

    response = await client.post(
        f"{user_role}/{user_id}/role",
        json=role_id_for_user)

    assert response.status_code == HTTPStatus.CREATED


async def test_read_roles(
    create_admin, create_role, client: AsyncClient, session: AsyncSession):

    await client.post(
        url_token,
        headers={'Content-Type': 'application/x-www-form-urlencoded', 'accept': 'application/json'},
        data=token_in)

    response = await client.get(roles)

    assert response.status_code == HTTPStatus.OK


async def test_delete_role(
    create_admin, create_role, client: AsyncClient, session: AsyncSession):

    await client.post(
        url_token,
        headers={'Content-Type': 'application/x-www-form-urlencoded', 'accept': 'application/json'},
        data=token_in)

    response = await client.delete(roles+'26acca1f-80eb-4cc4-a0de-2a160534f211')

    assert response.status_code == HTTPStatus.NO_CONTENT


async def test_change_role(
    create_admin, create_role, client: AsyncClient, session: AsyncSession):

    await client.post(
        url_token,
        headers={'Content-Type': 'application/x-www-form-urlencoded', 'accept': 'application/json'},
        data=token_in)

    response = await client.patch(roles+'26acca1f-80eb-4cc4-a0de-2a160534f211', json=put_role)

    assert response.status_code == HTTPStatus.OK


async def test_read_role(
    create_admin, create_role, client: AsyncClient, session: AsyncSession):

    login = await client.post(
        url_token,
        headers={'Content-Type': 'application/x-www-form-urlencoded', 'accept': 'application/json'},
        data=token_in)

    token = login.cookies.get('refresh_token')
    playload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    user_id = playload['uuid']

    response = await client.get(
        f"{roles}{user_id}/role/")

    assert response.status_code == HTTPStatus.OK


async def test_delete_created_role_for_user(
    create_admin, create_role, client: AsyncClient, session: AsyncSession):

    login = await client.post(
        url_token,
        headers={'Content-Type': 'application/x-www-form-urlencoded', 'accept': 'application/json'},
        data=token_in)

    token = login.cookies.get('refresh_token')
    playload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    user_id = playload['uuid']

    await client.post(
        f"{user_role}/{user_id}/role",
        json=role_id_for_user)

    response = await client.delete(
        f"{roles}{user_id}/role/")

    assert response.status_code == HTTPStatus.NO_CONTENT