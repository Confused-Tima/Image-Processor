from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.configs import settings
from app.middlewares import middlewares
from redis_connection import RedisConnection


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
def health_check():
    return {"status": "Healthy"}


app.include_router()
