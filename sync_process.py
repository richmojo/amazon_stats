from db import sync_asins
import time


def sync_process():
    while True:
        sync_asins()
        time.sleep(600)


if __name__ == "__main__":
    while True:
        try:
            sync_process()
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(600)
