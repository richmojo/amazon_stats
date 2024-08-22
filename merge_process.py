from db import merge_product_data_batch, merge_a2a_product_data_batch
import time


def merge_process():
    while True:
        products_response = merge_product_data_batch()
        a2a_response = merge_a2a_product_data_batch()

        if not products_response and not a2a_response:
            time.sleep(60)

        time.sleep(1)


if __name__ == "__main__":
    merge_process()
