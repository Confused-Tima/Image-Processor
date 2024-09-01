from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from app.configs import settings
from app.routes import add_compress_job
from app.middlewares import middlewares
from redis_connection import RedisConnection
from app.security.authenticate import authenticate_api_key


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Handles the tasks which needs to be started before fastapi app
    and closed after closing of the app
    """
    redis_conn = RedisConnection()
    yield
    redis_conn.shutdown()


# App starts here
app = FastAPI(lifespan=lifespan, middleware=middlewares)


@app.get(f"{settings.api_prefix}/v1/health-check")
def health_check(_=Depends(authenticate_api_key)):
    """API for app health check"""

    return {"status": "Healthy"}


app.include_router(add_compress_job.router, prefix=settings.api_prefix)
