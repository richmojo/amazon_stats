from db import delete_asins
import time


def delete_process():
    while True:
        try:
            delete_asins()
            time.sleep(60)  # Adjust sleep time as necessary
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(60)


if __name__ == "__main__":
    while True:
        try:
            delete_process()
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(60)
