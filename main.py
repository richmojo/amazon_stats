import time
from amazon_data import AmazonData

# create a docker run, update


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
