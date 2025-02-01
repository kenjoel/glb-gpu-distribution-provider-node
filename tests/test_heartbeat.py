# test_heartbeat.py
from app.heartbeat import heartbeat_loop
import threading
import time

def main():
    # For test purposes, pass a dummy provider_id.
    dummy_provider_id = "dummy_provider_id"
    # Run the heartbeat loop in a separate thread.
    hb_thread = threading.Thread(target=heartbeat_loop, args=(dummy_provider_id,), daemon=True)
    hb_thread.start()

    # Let it run for 2 or 3 cycles (e.g., 90 seconds).
    time.sleep(90)
    print("Heartbeat test complete.")

if __name__ == "__main__":
    main()
