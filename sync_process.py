from db import sync_asins
import time


def sync_process():
    """
    Synchronizes ASINs from sourcing_products to amazon_data table via amazon_asins.

    This function triggers a PostgreSQL stored procedure that:
    1. Identifies products in sourcing_products that need processing:
       - Products with ASINs not yet in amazon_data
       - Products with data older than 24 hours
       - Products not marked as 'sourced' or 'checked'
    2. Extracts unique ASINs from these products' raw_products JSON
    3. Inserts these ASINs into amazon_asins table (ignoring duplicates)

    The amazon_asins table likely serves as a queue for another process
    that will fetch the actual Amazon product data.

    Raises:
        Exception: Any database or processing errors are caught and printed
    """
    try:
        sync_asins()
    except Exception as e:
        print(f"Error in sync process: {e}")
        return


if __name__ == "__main__":
    while True:
        sync_process()
        time.sleep(60 * 5) 
