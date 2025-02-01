# tests/test_config.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings

def main():
    print("Provider Name:", settings.PROVIDER_NAME)
    print("GPU Model:", settings.GPU_MODEL)
    print("Total VRAM:", settings.TOTAL_VRAM)
    print("Region:", settings.REGION)

if __name__ == "__main__":
    main()
