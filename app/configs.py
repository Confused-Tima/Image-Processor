import os

from pydantic_settings import BaseSettings


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

    api_key_name: str = "x-api-key"
    api_key: str | None = None

    # Log file name
    log_file: str = "api.log"

    @property
    def log_dir(self) -> str:
        return (
            "/logs"
            if self.is_virtual_env
            else os.path.join(os.getcwd(), "logs")
        )

    # API request/response logger format
    req_logging_string: str = "METHOD: {0}, REQUEST URL: {1}"
    res_logging_string: str = """
        RESPONSE STATUS: {0}, TIME TAKEN: {1:.4f} secs, REQUEST URL: {2}
    """

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


# Initialize the settings
settings = MainSettings()
