from core.config import yandex_auth_config
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import RedirectResponse
from services.auth_service import AuthService, get_auth_service
from services.ya_service import get_oauth_service, OauthService
from services.auth_external import get_YandexSignIn, OAuthSignIn

router = APIRouter()

debug_token_url = f'https://oauth.yandex.ru/authorize?response_type=token&client_id={yandex_auth_config.client_id}'
login_url = "https://login.yandex.ru/info?"


@router.get("/ya_auth_token",
            summary="получить отладочный токен яндекс",
            tags=["вход через социальные сервисы"],
            status_code=status.HTTP_307_TEMPORARY_REDIRECT, )
async def get_yandex_token():
    return RedirectResponse(
        debug_token_url)

@router.get("/ya_auth",
            summary="войти через акканут яндекса c помощью отладочного токена",
            tags=["вход через социальные сервисы"],)
async def get_yandex_auth(access_token: str,
                          response: Response,
                          request: Request,
                          service: AuthService = Depends(get_auth_service),
                          ya_service: OauthService = Depends(get_oauth_service)):

    user_info = await ya_service.get_user_info(login_url, access_token)
    login = user_info.get("login", None)
    social_id = user_info.get("psuid", None)

    social_account = await ya_service.get_social_account(
        social_id=social_id, social_name="yandex")

    user_agent = request.headers.get("user-agent")

    if social_account is not None:
        user = await ya_service.get_user_by_id(social_account.user_id)
    else:
        user = await ya_service.get_user_by_email(username=login)

        if user is None:
            user = await ya_service.create_user(username=login)
            social_account = await ya_service.create_social_account(
                social_id=social_id, social_name="yandex", user_id=user.uuid)

    user_id = user.uuid

    refresh_token_check = await service.check_refresh_token(
            user_id=user_id, user_agent=user_agent)

    if refresh_token_check:
        await service.delete_refresh_token(
            refresh_token_check.refresh_token)

    tokens = await service.create_tokens(
            db_user=user, user_agent=user_agent)

    response.set_cookie(
                key="refresh_token", httponly=True, value=tokens["refresh_token"])
    response.set_cookie(
                key="Authorization", httponly=True, value=f"Bearer {tokens['access_token']}")

    return {"access_token": access_token,
            "user_info": user_info,
            "message": "Successfully logged in"}

@router.get("/authorize/{provider}/",
            summary="вход через социальные сервисы (в настоящий момент только яндекс)",
            tags=["вход через социальные сервисы"],)
def authorize(request: Request, provider: str):
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize(request)


@router.get("/callback/{provider}/",
            tags=["вход через социальные сервисы"],)
async def oauth_callback(request: Request,
                         provider: str,
                         debug_token: str,
                         response: Response,
                         service: AuthService = Depends(get_auth_service),
                         oauth_service: OauthService = Depends(get_oauth_service)):
    oauth = OAuthSignIn.get_provider(provider)

    user_info = await oauth.callback(request, debug_token)

    login = user_info.get("login", None)
    social_id = user_info.get("psuid", None)

    social_account = await oauth_service.get_social_account(
        social_id=social_id, social_name="yandex")

    user_agent = request.headers.get("user-agent")

    if social_account is not None:
        user = await oauth_service.get_user_by_id(social_account.user_id)
    else:
        user = await oauth_service.get_user_by_email(username=login)

        if user is None:
            user = await oauth_service.create_user(username=login)
            social_account = await oauth_service.create_social_account(
                social_id=social_id, social_name="yandex", user_id=user.uuid)

    user_id = user.uuid

    refresh_token_check = await service.check_refresh_token(
            user_id=user_id, user_agent=user_agent)

    if refresh_token_check:
        await service.delete_refresh_token(
            refresh_token_check.refresh_token)

    tokens = await service.create_tokens(
            db_user=user, user_agent=user_agent)

    response.set_cookie(
                key="refresh_token", httponly=True, value=tokens["refresh_token"])
    response.set_cookie(
                key="Authorization", httponly=True, value=f"Bearer {tokens['access_token']}")

    return {"user_info": user_info,
            "message": "Successfully logged in"}