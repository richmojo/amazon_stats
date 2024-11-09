from db import (
    merge_product_data_batch,
    merge_a2a_product_data_batch,
    merge_reverse_sourcing_data_batch,
)
import time


def merge_process():
    while True:
        try:
            products_response = merge_product_data_batch()
            a2a_response = merge_a2a_product_data_batch()
            reverse_sourcing_response = merge_reverse_sourcing_data_batch()

            if not all([products_response, a2a_response, reverse_sourcing_response]):
                time.sleep(600)

            time.sleep(1)
        except Exception as e:
            print(f"Error in merge process: {e}")
            time.sleep(600)


if __name__ == "__main__":
    try:
        while True:
            try:
                merge_process()
            except Exception as e:
                print(f"An error occurred: {e}")
                time.sleep(600)
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
