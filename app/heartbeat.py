# worker_node/app/heartbeat.py
import time
import requests
import logging
from .config import settings

logger = logging.getLogger(__name__)


def heartbeat_loop(provider_id):
    """
    Periodically sends a heartbeat to the Master Node.
    Adjust your endpoint as needed.
    """
    url = f"{settings.MASTER_NODE_URL}/providers/heartbeat"
    while True:
        try:
            resp = requests.post(url, json={"provider_id": str(provider_id)}, timeout=5)
            if resp.status_code == 200:
                logger.debug("Heartbeat OK")
            else:
                logger.warning(f"Heartbeat failed: {resp.status_code}, {resp.text}")
        except requests.RequestException as e:
            logger.error(f"Heartbeat error: {e}")
        time.sleep(30)
