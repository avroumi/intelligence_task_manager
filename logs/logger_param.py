import logging 
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent / "app.log"

logging.basicConfig(
    format=" %(asctime)s |%(levelname)s | %(message)s ",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ],
    level=logging.INFO,
    force=True
)

logger = logging.getLogger(__name__)