# test_execute_job.py
from app.job_runner import execute_job

def main():
    # Define a dummy job matching the expected schema.
    dummy_job = {
        "id": "job_123",
        "command": "echo 'Hello from job!'",
        "docker_image": "alpine",
        "gpus": [0]
    }
    execute_job(dummy_job)

if __name__ == "__main__":
    main()
