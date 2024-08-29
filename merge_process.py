from db import merge_product_data_batch, merge_a2a_product_data_batch
import time


def merge_process():
    while True:
        try:
            products_response = merge_product_data_batch()
            a2a_response = merge_a2a_product_data_batch()

            if not products_response and not a2a_response:
                time.sleep(600)

            time.sleep(1)
        except:
            time.sleep(600)


if __name__ == "__main__":
    while True:
        try:
            merge_process()
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(600)
