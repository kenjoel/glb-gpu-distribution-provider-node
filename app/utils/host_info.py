# app/utils/host_info.py

import socket
import GPUtil
import requests

def get_gpu_info():
    """
    Returns a tuple (gpu_model, total_vram) for the first available GPU.
    If no GPU is found, returns (None, None).
    """
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            return None, None
        # For simplicity, pick the first GPU.
        gpu = gpus[0]
        gpu_model = gpu.name
        # GPUtil returns memory in MB.
        total_vram = int(gpu.memoryTotal)
        return gpu_model, total_vram
    except Exception as e:
        print(f"Error detecting GPU info: {e}")
        return None, None

def get_provider_name():
    """
    Use the system hostname as the provider name.
    """
    try:
        return socket.gethostname()
    except Exception as e:
        print(f"Error getting hostname: {e}")
        return "UnknownProvider"

def get_location():
    """
    Get approximate geolocation info based on the external IP address.
    This example uses the ip-api.com service.
    Returns a dictionary with keys: country, regionName, city, lat, lon.
    If the request fails, returns an empty dictionary.
    """
    try:
        response = requests.get("http://ip-api.com/json", timeout=5)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        if data.get("status") == "success":
            return {
                "country": data.get("country"),
                "region": data.get("regionName"),
                "city": data.get("city"),
                "lat": data.get("lat"),
                "lon": data.get("lon"),
            }
        else:
            print("Geolocation lookup unsuccessful:", data.get("message"))
            return {}
    except Exception as e:
        print(f"Error getting geolocation: {e}")
        return {}

# Optional: a helper function to gather all host info
def get_host_info():
    """
    Gather and return all available host info as a dictionary.
    """
    gpu_model, total_vram = get_gpu_info()
    provider_name = get_provider_name()
    location = get_location()

    return {
        "provider_name": provider_name,
        "gpu_model": gpu_model,
        "total_vram": total_vram,
        "location": location,
    }

# If running this module directly for testing, print the host info.
if __name__ == "__main__":
    info = get_host_info()
    print("Host Information:")
    print(info)
