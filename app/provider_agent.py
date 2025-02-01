# worker_node/app/provider_agent.py

import requests
import logging
from .config import settings

logger = logging.getLogger(__name__)


def register_provider():
    """
    Call the Master Node's /providers/register endpoint.
    """
    url = f"{settings.MASTER_NODE_URL}/providers/register"
    headers = {
        "Authorization": f"Bearer {settings.PROVIDER_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": settings.PROVIDER_NAME,
        "secret_token": settings.PROVIDER_SECRET,
        "gpu_model": settings.GPU_MODEL,
        "total_vram": settings.TOTAL_VRAM,
        "region": settings.REGION
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        print("The data being posted is", payload, headers)
        resp.raise_for_status()
        provider_data = resp.json()
        logger.info(f"Successfully registered providers: {provider_data.detail}")
        return provider_data
    except requests.RequestException as e:
        logger.error(f"Provider registration failed: {e}")
        return None


def report_usage(provider_id, job_id, gpu_util, mem_usage):
    """
    Example usage reporting: calls /usage/report with some metrics.
    Adjust to match your real endpoint signature.
    """
    url = f"{settings.MASTER_NODE_URL}/usage/report"
    payload = {
        "provider_id": str(provider_id),
        "job_id": str(job_id),
        "gpu_util": gpu_util,
        "mem_usage": mem_usage
    }
    try:
        resp = requests.post(url, json=payload, timeout=5)
        resp.raise_for_status()
        logger.info(f"Usage reported for job {job_id}")
    except requests.RequestException as e:
        logger.error(f"Failed usage report for job {job_id}: {e}")
