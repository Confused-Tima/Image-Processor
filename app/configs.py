import os
from enum import Enum

from pydantic_settings import BaseSettings


class RQueues(Enum):
    IMAGE_PROCESSING_Q = os.getenv("IMAGE_PROCESSING_Q", "image_processing_q")


class MainSettings(BaseSettings):
    """
    Main project settings.
    Reads the environment variables from .env file and
    updates them at the start of the app
    If not present then the default is applied
    """

    is_virtual_env: bool = False  # Variable to know if inside docker
    is_debug_mode: bool = False  # If in debug mode
    api_prefix: str = "/api"

    # Redis settings
    redis_host: str = "localhost"
    redis_port: str = "6379"
    redis_db: str = "0"

    @property
    def redis_url(self) -> str:
        return "redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # How long are we going to persist the results(for retrieval)
    results_persistance: int = 50 * 24 * 60 * 60

    # How long do a job gets to run after dequeue (default 180s)
    job_timeout: int = 24 * 60 * 60

    api_key_name: str = "x-api-key"
    api_key: str | None = None

    # Log file name
    log_file: str = "api.log"

    @property
    def log_dir(self) -> str:
        return (
            "/logs"
            if self.is_virtual_env
            else os.path.join(os.getcwd(), "api", "logs")
        )

    # API request/response logger format
    req_logging_string: str = "METHOD: {0}, REQUEST URL: {1}"
    res_logging_string: str = """
        RESPONSE STATUS: {0}, TIME TAKEN: {1:.4f} secs, REQUEST URL: {2}
    """

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extras = "allow"


# Initialize the settings
settings = MainSettings()
