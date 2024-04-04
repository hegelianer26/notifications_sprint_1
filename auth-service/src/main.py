import logging
from contextlib import asynccontextmanager

import uvicorn
from api.v1 import auth, roles, users, ya_auth, groups
from core.config import fastapi_config, redis_config
from core.logger import LOGGING
from core.tracer import configure_tracer
from db import redis
from db.sql.database import create_database
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from fastapi_redis_rate_limiter import RedisClient, RedisRateLimiterMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


redis_host = redis_config.redis_host
redis_port = redis_config.redis_port
redis.redis = Redis(host=redis_host, port=redis_port, decode_responses=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if fastapi_config.is_debug:
        await create_database()
    await redis.redis
    yield

if fastapi_config.tracer_enabled:
    configure_tracer()

app = FastAPI(
    title=fastapi_config.fastapi_project_name,
    docs_url="/auth/api/openapi",
    openapi_url="/auth/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

FastAPIInstrumentor.instrument_app(app)


if fastapi_config.limiter_enabled:
    redis_client = RedisClient(host=redis_host, port=redis_port, db=0)
    app.add_middleware(
        RedisRateLimiterMiddleware, redis_client=redis_client, limit=40, window=60)


# @app.middleware('http')
# async def before_request(request: Request, call_next):
#     response = await call_next(request)
#     request_id = request.headers.get('X-Request-Id')
#     if not request_id:
#         return ORJSONResponse(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             content={'detail': 'X-Request-Id is required'})
#     return response



app.include_router(roles.router, prefix="/auth/api/v1/roles")
app.include_router(users.router, prefix="/auth/api/v1/users")
app.include_router(auth.router, prefix="/auth/api/v1/auth")
app.include_router(ya_auth.router, prefix="/auth/api/v1/oauth")
app.include_router(groups.router, prefix="/auth/api/v1/groups")



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8081,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True
    )
