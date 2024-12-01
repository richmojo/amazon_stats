from db import sync_asins
import time


def sync_process():
    try:
        sync_asins()
    except Exception as e:
        print(f"Error in sync process: {e}")
        time.sleep(600)


if __name__ == "__main__":
    sync_process()
