from db import (
    merge_product_data_batch,
    merge_a2a_product_data_batch,
    merge_reverse_sourcing_data_batch,
)
import time


def merge_process():
    """
    Merges Amazon data into the sourcing products table by running three separate merge operations:

    1. Product Data Merge (merge_product_data_batch):
       - Processes standard sourcing products that need Amazon data
       - Updates products with Amazon fees, prices, and metrics
       - Calculates FBA/FBM profits and ROI for each ASIN
       - Updates product status from 'need_amazon_data' to 'need_filtering'

    2. A2A (Amazon-to-Amazon) Merge (merge_a2a_product_data_batch):
       - Similar to standard merge but for Amazon-to-Amazon products
       - Processes products where source and target are both Amazon

    3. Reverse Sourcing Merge (merge_reverse_sourcing_data_batch):
       - Processes reverse sourcing products
       - Updates Amazon data for products found on other marketplaces

    The process runs continuously until one of the merge operations returns False,
    indicating no more products need processing, or until an exception occurs.

    Each iteration includes a 1-second delay to prevent overloading the database.

    Returns:
        None

    Raises:
        Catches and prints any exceptions that occur during the merge process
    """
    while True:
        try:
            products_response = merge_product_data_batch()
            a2a_response = merge_a2a_product_data_batch()
            reverse_sourcing_response = merge_reverse_sourcing_data_batch()

            if not any([products_response, a2a_response, reverse_sourcing_response]):
                return

            time.sleep(1)
        except Exception as e:
            print(f"Error in merge process: {e}")
            return


if __name__ == "__main__":
    while True:
        merge_process()
        time.sleep(60 * 5)
