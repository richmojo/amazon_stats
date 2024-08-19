from db import merge_product_data_batch
import time


def merge_process():
    while True:
        response = merge_product_data_batch()
        if not response:
            time.sleep(60)
        time.sleep(1)


if __name__ == "__main__":
    merge_process()
