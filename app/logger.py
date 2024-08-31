import os

from app.configs import settings
from main_logger import get_timed_rotating_file_logger


log_dir = os.makedirs(settings.log_dir, exist_ok=True)
log_file = os.path.join(log_dir, settings.log_file)


logger = get_timed_rotating_file_logger(
    "API", log_file
)
