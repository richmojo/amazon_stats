from db import sync_asins
import time


def sync_process():
    while True:
        sync_asins()
        time.sleep(60)  # Adjust sleep time as necessary


if __name__ == "__main__":
    sync_process()
