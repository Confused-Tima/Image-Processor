from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from app.configs import settings
from app.middlewares import middlewares
from redis_connection import RedisConnection
from app.security import authenticate


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
def health_check(_=Depends(authenticate)):
    """API for app health check"""

    return {"status": "Healthy"}


app.include_router()
