import os
import sys
import logging
import threading
import subprocess

from .config import settings
from .provider_agent import register_provider
from .heartbeat import heartbeat_loop


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    logger = logging.getLogger("WorkerNode")

    # 1) Register with Master Node
    provider_data = register_provider()
    if not provider_data:
        logger.error("Could not register provider. Exiting.")
        sys.exit(1)

    provider_id = provider_data["id"]

    # 2) Start a heartbeat thread if desired
    hb_thread = threading.Thread(target=heartbeat_loop, args=(provider_id,), daemon=True)
    hb_thread.start()

    # 3) Start Ray in worker mode
    # We'll run "ray start --address=RAY_HEAD_IP:6379 --num-gpus=..."
    ray_cmd = [
        "ray", "start",
        f"--address={settings.RAY_HEAD_IP}:{settings.RAY_HEAD_PORT}",
        f"--num-gpus={settings.NUM_GPUS}"
    ]
    logger.info(f"Starting Ray worker: {' '.join(ray_cmd)}")

    try:
        # This will block until Ray starts or fails
        subprocess.check_call(ray_cmd)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start Ray worker node: {e}")
        sys.exit(1)

    logger.info("Ray worker node started successfully. Now blocking...")

    # 4) Keep the script alive so the container doesn't exit
    # In real usage, you might want to monitor Ray or handle signals gracefully
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logger.info("Exiting worker node...")


if __name__ == "__main__":
    main()
