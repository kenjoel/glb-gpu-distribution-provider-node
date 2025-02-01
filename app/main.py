# provider_node/app/main.py

import logging
import threading
import time
import subprocess
import sys

from app.config import settings
from app.provider_agent import register_provider
from app.heartbeat import heartbeat_loop
from app.job_runner import job_polling_loop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ProviderNode")

def start_ray_worker():
    ray_cmd = [
        "ray", "start",
        f"--address={settings.RAY_HEAD_IP}:{settings.RAY_HEAD_PORT}",
        f"--num-gpus={settings.NUM_GPUS}"
    ]
    logger.info(f"Starting Ray worker: {' '.join(ray_cmd)}")
    try:
        subprocess.check_call(ray_cmd)
        logger.info("Ray worker node started successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start Ray worker node: {e}")
        sys.exit(1)

def main():
    # 1. Register with the master node.
    provider_data = register_provider()
    if not provider_data:
        logger.error("Provider registration failed. Exiting.")
        sys.exit(1)
    provider_id = provider_data["id"]

    # 2. Start the heartbeat thread.
    hb_thread = threading.Thread(target=heartbeat_loop, args=(provider_id,), daemon=True)
    hb_thread.start()

    # 3. Start Ray worker (if needed).
    start_ray_worker()

    # 4. Start the job polling loop in a separate thread.
    job_thread = threading.Thread(target=job_polling_loop, daemon=True)
    job_thread.start()

    # 5. Keep the main thread alive.
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("Shutting down provider node...")

if __name__ == "__main__":
    main()
