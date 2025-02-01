# worker.py

import os
import time
import requests
import docker
import subprocess
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from config.env file
load_dotenv(dotenv_path='./config.env')

# Replace with your actual server endpoint
SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:8000')

# Docker client
client = docker.from_env()

def fetch_job():
    """Simulate fetching a job from the server."""
    try:
        response = requests.get(f'{SERVER_URL}/jobs/assign')
        response.raise_for_status()  # Raise HTTPError for non-200 status codes
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching job: {e}")
        return None

def execute_job(job):
    """Execute job using Docker with GPU support and monitor GPU usage."""
    try:
        logger.info(f"Starting job: {job['id']}, command: {job['command']}")

        # Define GPU devices to be used by the container
        gpu_devices = [f'nvidia:{gpu}' for gpu in job.get('gpus', [])]  # job['gpus'] should be a list of GPU indices

        # Run job in a Docker container with GPU support
        container = client.containers.run(
            image=job['docker_image'],
            command=job['command'],
            runtime="nvidia",     # Use NVIDIA runtime for GPU support
            devices=gpu_devices,  # Specify GPU devices
            remove=True,          # Remove container after execution
            detach=True           # Run container in the background
        )

        # Monitor GPU usage during job execution
        gpu_stats = monitor_gpu(container)

        # Wait for container to finish
        exit_code = container.wait()['StatusCode']
        logger.info(f"Job {job['id']} completed with exit code: {exit_code}")

        # Report job completion and GPU metrics
        report_metrics(job['id'], gpu_stats)

    except docker.errors.DockerException as e:
        logger.error(f"Error running Docker container: {e}")
    except requests.RequestException as e:
        logger.error(f"Error during job execution: {e}")


def monitor_gpu(container):
    """Monitor GPU usage using nvidia-smi for multiple GPUs."""
    try:
        gpu_stats = {}
        while True:
            # Query GPU utilization using nvidia-smi
            output = subprocess.check_output(['nvidia-smi', '--query-gpu=index,utilization.gpu,memory.total,memory.used,memory.free', '--format=csv,noheader,nounits'])

            # Process output to extract metrics for each GPU
            gpu_info = output.decode('utf-8').strip().split('\n')
            for line in gpu_info:
                gpu_index, gpu_utilization, memory_total, memory_used, memory_free = line.split(',')
                gpu_stats[int(gpu_index)] = {
                    'utilization': int(gpu_utilization),
                    'memory_total': int(memory_total),
                    'memory_used': int(memory_used),
                    'memory_free': int(memory_free),
                }

            # Check if container is still running
            if not container.status == 'running':
                break

            time.sleep(1)

        return gpu_stats

    except subprocess.CalledProcessError as e:
        logger.error(f"Error monitoring GPU: {e}")
        return {}


def report_metrics(job_id, gpu_stats):
    """Report job completion and GPU metrics to the server."""
    try:
        payload = {
            'job_id': job_id,
            'gpu_utilization': gpu_stats.get('utilization', 0),
            # Add more metrics as needed
        }
        response = requests.post(f'{SERVER_URL}/jobs/{job_id}/metrics', json=payload)
        response.raise_for_status()  # Raise HTTPError for non-200 status codes
        logger.info(f"Metrics reported successfully for job {job_id}.")
    except requests.RequestException as e:
        logger.error(f"Error reporting metrics for job {job_id}: {e}")

def main():
    logger.info("Worker node started.")

    while True:
        job = fetch_job()

        if job:
            execute_job(job)
        else:
            time.sleep(5)  # Poll every 5 seconds if no job found

if __name__ == "__main__":
    main()
