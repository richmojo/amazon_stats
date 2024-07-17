import time
from amazon_api import AmazonAPI
from db import get_asins, save_asins, merge_product_data_batch, sync_asins
from create_fees import create_fees

BATCH_SIZE = 20


class AmazonData:
    def __init__(self):
        self.api = AmazonAPI()

    def get_batches(self):
        asins = get_asins()
        print(f"Got {len(asins)} asins")

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

        time.sleep(2.0)

        fbm_fees_data = self.api.get_batch_fees(fbm_fees)

        if not fbm_fees_data:
            return fees_data

        for asin, details in fbm_fees_data.items():
            fees_data[asin] = details

        return fees_data

    def run(self):
        sync_asins()

        while True:
            updated_data = []
            batches = self.get_batches()

            if not batches:
                break

            for batch in batches:
                batch_asins = [asin["asin"] for asin in batch]
                data = self.get_product_details(batch_asins)
                run_time = int(time.time())

                if not data:
                    print("No data")
                    time.sleep(1.8)
                    continue

                fees_data = self.get_fees(data)

                for asin, details in data.items():
                    row = batch[batch_asins.index(asin)]
                    row["data"] = details

                    new_data = fees_data.get(asin, {})
                    row["data"].update(new_data)

                updated_data.extend(batch)

                sleep_time = 2 - (int(time.time()) - run_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)

            if updated_data:
                print(f"Updating {len(updated_data)} batches")
                save_asins(updated_data)

            sync_asins()

        while True:
            response = merge_product_data_batch()
            if not response:
                break

            time.sleep(1)

        return
