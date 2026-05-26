import os
import logging

from dotenv import load_dotenv

logging.basicConfig(
    level=0,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)

logger = logging.getLogger(__name__)

load_dotenv()

CLICKHOUSE_USER = os.environ.get("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.environ.get("CLICKHOUSE_PASSWORD", "")
CLICKHOUSE_DB = os.environ.get("CLICKHOUSE_DB", "default")
CLICKHOUSE_HOST = os.environ.get("CLICKHOUSE_HOST", "clickhouse")
CLICKHOUSE_PORT = int(os.environ.get("CLICKHOUSE_PORT", 8123))
SERVER_PORT = int(os.environ.get("SERVER_PORT", 9090))
SYMBOL = os.environ.get("SYMBOL", "BTCUSDT")
