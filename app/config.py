import os
from dotenv import load_dotenv
from app.utils.host_info import get_gpu_info, get_provider_name

load_dotenv()  # Load .env if present

class WorkerSettings:
    """
    Holds configuration for the worker node.
    """
    # Ray settings
    RAY_HEAD_IP = os.getenv("RAY_HEAD_IP", "127.0.0.1")
    RAY_HEAD_PORT = os.getenv("RAY_HEAD_PORT", "6379")
    NUM_GPUS = int(os.getenv("NUM_GPUS", "1"))

    # Master Node URL
    MASTER_NODE_URL = os.getenv("MASTER_NODE_URL", "https://002d-105-163-156-31.ngrok-free.app")

    # Provider registration token (from a secure source)
    PROVIDER_BEARER_TOKEN = os.getenv("PROVIDER_BEARER_TOKEN", "SUPER_SECURE_TOKEN_FOR_PROVIDERS")

    # Auto-detect provider details if not provided
    PROVIDER_NAME = os.getenv("PROVIDER_NAME", get_provider_name())
    PROVIDER_SECRET = os.getenv("PROVIDER_SECRET", "some_secret_for_my_node")

    # Auto-detect GPU info (if available)
    _detected_gpu_model, _detected_total_vram = get_gpu_info()
    GPU_MODEL = os.getenv("GPU_MODEL", _detected_gpu_model or "Unknown GPU")
    TOTAL_VRAM = int(os.getenv("TOTAL_VRAM", _detected_total_vram or 0))

    # Region: either provided or default to a value (auto-detection here is optional)
    REGION = os.getenv("REGION", "us-east-1")

settings = WorkerSettings()
