from contextlib import asynccontextmanager

import uvicorn
from core.config import fastapi_config
from db.postgres.database import create_database
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from api.v1 import notificat

@asynccontextmanager
async def lifespan(app: FastAPI):
    if fastapi_config.is_debug:
        await create_database()
    yield


app = FastAPI(
    title=fastapi_config.fastapi_project_name,
    docs_url="/notify/api/openapi",
    openapi_url="/notify/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

app.include_router(notificat.router)

# @app.middleware('http')
# async def before_request(request: Request, call_next):
#     response = await call_next(request)
#     request_id = request.headers.get('X-Request-Id')
#     if not request_id:
#         return ORJSONResponse(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             content={'detail': 'X-Request-Id is required'})
#     return response



# app.include_router(roles.router, prefix="/auth/api/v1/roles")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8082,
        reload=True
    )
