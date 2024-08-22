from db import delete_asins
import time


def delete_process():
    while True:
        delete_asins()
        time.sleep(60)  # Adjust sleep time as necessary


if __name__ == "__main__":
    delete_process()
