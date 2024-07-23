import time
from amazon_stats import AmazonData

# create a docker run, update
# change the fetch to get oldest updated_at first


def run():
    data_fetcher = AmazonData()
    data_fetcher.run()
    return


if __name__ == "__main__":
    while True:
        try:
            run()
        except Exception as e:
            print(e)

        time.sleep(60)
