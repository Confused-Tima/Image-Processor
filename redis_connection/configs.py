import os
from enum import Enum
from typing import Union
from datetime import datetime

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class CustomJobStatus(BaseModel):
    result: Union[str | None] = None
    created_at: Union[datetime | None] = None
    started_at: Union[datetime | None] = None
    ended_at: Union[datetime | None] = None
    error: Union[str | None] = None


class RQueues(Enum):
    IMAGE_PROCESSING_Q = os.getenv("IMAGE_PROCESSING_Q", "image_processing_q")


class RedisSettings(BaseSettings):
    redis_host: str = "localhost"
    redis_port: str = "6379"
    redis_db: str = "0"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # How long are we going to persist the results(for retrieval)
    results_persistance: int = 50 * 24 * 60 * 60

    # How long do a job gets to run after dequeue (default 180s)
    job_timeout: int = 24 * 60 * 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


redis_settings = RedisSettings()
