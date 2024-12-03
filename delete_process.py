from db import delete_asins
import time


def delete_process():
    try:
        delete_asins()
    except Exception as e:
        print(f"Error in delete process: {e}")
        return


if __name__ == "__main__":
    while True:
        delete_process()
        time.sleep(60 * 5)
