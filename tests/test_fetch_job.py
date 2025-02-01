# test_fetch_job.py
from app.job_runner import fetch_job


def main():
    job = fetch_job()
    if job:
        print("Fetched job:", job)
    else:
        print("No job fetched.")


if __name__ == "__main__":
    main()
