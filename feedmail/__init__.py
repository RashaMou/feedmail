import logging
import os

log_file_path = os.getenv("LOG_FILE_PATH", os.path.expanduser("~/feedmaillogs"))
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=log_level,
    handlers=[logging.FileHandler(log_file_path), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)
