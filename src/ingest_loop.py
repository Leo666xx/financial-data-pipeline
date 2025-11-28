import time
import signal
import sys
from ingest import ingest_once

running = True

def handle_sigint(signum, frame):
    global running
    running = False
    print("Received stop signal, exiting...")

signal.signal(signal.SIGINT, handle_sigint)
signal.signal(signal.SIGTERM, handle_sigint)

if __name__ == "__main__":
    symbol = "GBPUSD=X"
    interval = 60  # seconds
    print(f"Starting ingest loop for {symbol}, interval={interval}s")
    while running:
        try:
            ingest_once(symbol)
        except Exception as e:
            print("Ingest error:", e)
        # sleep with small granularity to react to signals
        for _ in range(int(interval)):
            if not running:
                break
            time.sleep(1)
    print("Ingest loop stopped")
