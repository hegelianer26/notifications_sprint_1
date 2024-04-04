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

test_user = {'username': 'admin1', 'password': 'admin1'}
admin_user = {'username': 'admin', 'password': 'admin'}

token_in = f"grant_type=&username=admin&password=admin&client_id=&client_secret="

url_login = f'/api/v1/auth/login/'
url_token = f'/api/v1/auth/token/'
url_out = f'/api/v1/auth/logout/'
url_users = f'/api/v1/users/'
url_me = f'/api/v1/users/me/'
url_history = f'/api/v1/users/me/history/'
url_user_info = f'/api/v1/users/'


async def test_create_user(client: AsyncClient, session: AsyncSession):
    response = await client.post(url_login, json=test_user)
    response_double = await client.post(url_login, json=test_user)
    assert response.status_code == HTTPStatus.CREATED
    assert response_double.status_code == HTTPStatus.BAD_REQUEST


async def test_read_me(create_admin, client: AsyncClient, session: AsyncSession):

    await client.post(
        url_token,
        headers={'Content-Type': 'application/x-www-form-urlencoded', 'accept': 'application/json'},
        data=token_in)

    response = await client.get(url_me)
    assert response.status_code == HTTPStatus.OK
    assert response.json()['username'] == 'admin'


async def test_read_history(create_admin, client: AsyncClient, session: AsyncSession):

    await client.post(
        url_token,
        headers={'Content-Type': 'application/x-www-form-urlencoded', 'accept': 'application/json'},
        data=token_in)

    response = await client.get(url_history)
    assert response.status_code == HTTPStatus.OK


async def test_get_token(create_admin, client: AsyncClient, session: AsyncSession):

    response = await client.post(
        url_token,
        headers={'Content-Type': 'application/x-www-form-urlencoded', 'accept': 'application/json'},
        data=token_in)
    assert response.status_code == HTTPStatus.OK
    token = response.cookies.get('Authorization')
    assert 'Bearer' in token


async def test_get_out(create_admin, client: AsyncClient, session: AsyncSession):

    await client.post(
        url_token,
        headers={'Content-Type': 'application/x-www-form-urlencoded', 'accept': 'application/json'},
        data=token_in)
    response = await client.post(url_out)
    token = response.cookies.get('Authorization')
    refresh_token = response.cookies.get('refresh_token')
    assert token == None
    assert refresh_token == None


async def test_root(client: AsyncClient, session: AsyncSession):
    response = await client.get(url_users)
    assert response.status_code == 200


async def test_get_decoded_token(
        create_admin, client: AsyncClient, session: AsyncSession):

    response = await client.post(
        url_token,
        headers={'Content-Type': 'application/x-www-form-urlencoded', 'accept': 'application/json'},
        data=token_in)

    token = response.cookies.get('refresh_token')
    playload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    assert len(playload) == 11


async def test_require_admin_role(
        client: AsyncClient, session: AsyncSession):
    session = session
    user_admin = User(username="admin", password="admin")
    user_admin.is_admin = False
    session.add(user_admin)
    await session.commit()

    login = await client.post(
        url_token,
        headers={'Content-Type': 'application/x-www-form-urlencoded', 'accept': 'application/json'},
        data=token_in)

    token = login.cookies.get('refresh_token')
    playload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    user_id = playload['uuid']
    response = await client.get(url_user_info+user_id)

    assert response.status_code == 403


async def test_require_admin_role_for_user_info(
        create_admin, client: AsyncClient, session: AsyncSession):

    login = await client.post(
        url_token,
        headers={'Content-Type': 'application/x-www-form-urlencoded', 'accept': 'application/json'},
        data=token_in)

    token = login.cookies.get('refresh_token')
    playload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    user_id = playload['uuid']
    response = await client.get(url_user_info+user_id)

    assert response.status_code == 200


async def test_change_my_info(create_admin, client: AsyncClient, session: AsyncSession):

    await client.post(
        url_token,
        headers={'Content-Type': 'application/x-www-form-urlencoded', 'accept': 'application/json'},
        data=token_in)

    response = await client.get(url_me)
    assert response.status_code == HTTPStatus.OK
    assert response.json()['username'] == 'admin'