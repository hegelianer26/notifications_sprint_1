from core.config import external_auth
from fastapi import Request
from rauth import OAuth2Service
from fastapi.responses import RedirectResponse
from functools import lru_cache
import aiohttp
from fastapi import APIRouter, Depends


router = APIRouter()


class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = external_auth['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['client_id']
        self.consumer_secret = credentials['client_secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self, request: Request):
        return request.url_for('oauth_callback', provider=self.provider_name)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]


class YandexSignIn(OAuthSignIn):
    def __init__(self):
        super().__init__('yandex')
        self.service = OAuth2Service(
            name='yandex',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://oauth.yandex.ru/authorize',
            access_token_url='https://login.yandex.ru/info',
            base_url='https://oauth.yandex.ru/'
        )

    def authorize(self, request: Request):
        authorization_url = self.service.get_authorize_url(
            response_type='token',
        )
        return RedirectResponse(url=authorization_url)

    async def callback(self, request: Request, debug_token: str = None):
        if debug_token is not None:
            session = aiohttp.ClientSession()
            async with session.post(url='https://login.yandex.ru/info?',
                                    headers={"Authorization": f'OAuth {debug_token}',
                                            'format': 'json | xml | jwt'},) as resp:
                user_info = await resp.json()
            await session.close()
            return user_info

        if 'code' not in request.query_params:
            return None
        data = {
            'code': request.query_params['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': self.get_callback_url(),
        }
        oauth_session = self.service.get_auth_session(data=data)
        me = oauth_session.get('user_info').json()
        return me


@lru_cache()
def get_YandexSignIn() -> YandexSignIn:
    return YandexSignIn()