# provider_node/app/job_runner.py

import time
import logging
import requests
import docker
import subprocess
from app.config import settings

logger = logging.getLogger(__name__)
client = docker.from_env()

SERVER_URL = settings.MASTER_NODE_URL  # Assuming same server for jobs

def fetch_job():
    """Fetch a job from the server."""
    try:
        response = requests.get(f'{SERVER_URL}/jobs/assign', timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching job: {e}")
        return None

def execute_job(job):
    """Execute a job using Docker with GPU support."""
    try:
        logger.info(f"Starting job {job['id']}: {job['command']}")

        gpu_devices = [f'nvidia:{gpu}' for gpu in job.get('gpus', [])]  # List of GPU indices.
        container = client.containers.run(
            image=job['docker_image'],
            command=job['command'],
            runtime="nvidia",
            devices=gpu_devices,
            remove=True,
            detach=True
        )

        gpu_stats = monitor_gpu(container)
        exit_code = container.wait()['StatusCode']
        logger.info(f"Job {job['id']} finished with exit code {exit_code}")
        report_metrics(job['id'], gpu_stats)
    except docker.errors.DockerException as e:
        logger.error(f"Error executing job {job['id']}: {e}")

def monitor_gpu(container):
    """Monitor GPU usage while the container is running."""
    gpu_stats = {}
    try:
        while container.status == 'running':
            output = subprocess.check_output(
                ['nvidia-smi', '--query-gpu=index,utilization.gpu,memory.total,memory.used,memory.free', '--format=csv,noheader,nounits'],
                text=True
            )
            for line in output.strip().split('\n'):
                gpu_index, gpu_util, mem_total, mem_used, mem_free = line.split(',')
                gpu_stats[int(gpu_index)] = {
                    'utilization': int(gpu_util.strip()),
                    'memory_total': int(mem_total.strip()),
                    'memory_used': int(mem_used.strip()),
                    'memory_free': int(mem_free.strip()),
                }
            time.sleep(1)
            container.reload()  # Refresh container status.
            if container.status != 'running':
                break
    except subprocess.CalledProcessError as e:
        logger.error(f"GPU monitoring error: {e}")
    return gpu_stats

def report_metrics(job_id, gpu_stats):
    """Report job metrics back to the master node."""
    payload = {
        'job_id': job_id,
        'gpu_stats': gpu_stats
    }
    try:
        response = requests.post(f'{SERVER_URL}/jobs/{job_id}/metrics', json=payload, timeout=5)
        response.raise_for_status()
        logger.info(f"Metrics reported for job {job_id}.")
    except requests.RequestException as e:
        logger.error(f"Error reporting metrics for job {job_id}: {e}")

def job_polling_loop():
    """Continuously poll for new jobs and execute them."""
    while True:
        job = fetch_job()
        if job:
            execute_job(job)
        else:
            time.sleep(5)  # Wait before polling again.
