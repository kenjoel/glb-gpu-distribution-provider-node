# Use a base image that has CUDA, or you can install GPU drivers in the container:
FROM nvidia/cuda:11.7.1-runtime-ubuntu22.04

# Install system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip wget curl \
    && rm -rf /var/lib/apt/lists/*

# Set the working dir
WORKDIR /worker_node

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the app code
COPY app/ ./app/

# Expose Ray's default ports if you want (or might do it via Docker run)
EXPOSE 8265
EXPOSE 6379

# Default command
CMD ["python3", "-m", "app.worker_main"]
