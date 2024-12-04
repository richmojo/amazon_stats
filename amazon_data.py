import time
import logging
from amazon_api import AmazonAPI
from db import get_asins, save_asins, merge_product_data_batch, sync_asins
from create_fees import create_fees
from datetime import datetime


BATCH_SIZE = 20
SLEEP_TIME = 2.5


class AmazonData:
    def __init__(self):
        self.api = AmazonAPI()
        self._setup_logging()
        self.product_sourced_today = 0

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.logger = logging.getLogger(__name__)

    def get_batches(self):
        asins = get_asins()

        if not asins:
            return []

        return [asins[i : i + BATCH_SIZE] for i in range(0, len(asins), BATCH_SIZE)]

    def get_product_details(self, batch_asins):
        return self.api.get_batch_product_details(batch_asins)

    def get_fees(self, data):
        fees = create_fees(data, fba=True)
        if not fees:
            return {}

        fees_data = self.api.get_batch_fees(fees)

        if not fees_data:
            return {}

        successful_asins = list(fees_data.keys())
        fbm_data = {k: v for k, v in data.items() if k not in successful_asins}

        if not fbm_data:
            return fees_data

        fbm_fees = create_fees(fbm_data, fba=False)

        time.sleep(SLEEP_TIME)

        if not fbm_fees:
            return fees_data

        fbm_fees_data = self.api.get_batch_fees(fbm_fees)

        if not fbm_fees_data:
            return fees_data

        for asin, details in fbm_fees_data.items():
            fees_data[asin] = details

        return fees_data

    def run(self):
        self.logger.info("Starting Amazon Data sync...")
        while True:
            updated_data = []
            batches = self.get_batches()

            if not batches:
                self.logger.info("No batches found, ending sync")
                break

            for batch_num, batch in enumerate(batches, 1):
                batch_asins = [asin["asin"] for asin in batch]

                data = self.get_product_details(batch_asins)
                run_time = int(time.time())

                if not data:
                    self.logger.warning(f"No data received for batch {batch_num}")
                    time.sleep(SLEEP_TIME)
                    continue

                fees_data = self.get_fees(data)

                for asin, details in data.items():
                    row = batch[batch_asins.index(asin)]
                    row["data"] = details

                    new_data = fees_data.get(asin, {})

                    row["data"].update(new_data)

                updated_data.extend(batch)

                sleep_time = SLEEP_TIME - (int(time.time()) - run_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)

            if updated_data:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.product_sourced_today += len(updated_data)
                self.logger.info(
                    f"[{current_time}] Updating {len(updated_data)} batches"
                )
                self.logger.info(
                    f"Products sourced today: {self.product_sourced_today}"
                )
                # add empty data if its not there
                for row in updated_data:
                    if "data" not in row:
                        row["data"] = {}

                save_asins(updated_data)
                self.product_sourced_today += len(updated_data)

                # Reset counter at midnight
                if datetime.now().hour == 0 and datetime.now().minute == 0:
                    self.logger.info(
                        f"Resetting daily counter. Previous count: {self.product_sourced_today}"
                    )
                    self.product_sourced_today = 0
