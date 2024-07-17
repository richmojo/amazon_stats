from sp_api.api import Products, ProductFees
from sp_api.base import Marketplaces

import os, time
from dotenv import load_dotenv
from typing import List

load_dotenv()

SP_API_ACCESS_KEY = os.getenv("SP_API_ACCESS_KEY")
SP_API_SECRET_KEY = os.getenv("SP_API_SECRET_KEY")
SP_API_ROLE_ARN = os.getenv("SP_API_ROLE_ARN")
SP_API_CLIENT_ID = os.getenv("SP_API_CLIENT_ID")
SP_API_CLIENT_SECRET = os.getenv("SP_API_CLIENT_SECRET")
SP_API_REFRESH_TOKEN = os.getenv("SP_API_REFRESH_TOKEN")
AWS_REGION = os.getenv("AWS_REGION")

credentials = {
    "refresh_token": SP_API_REFRESH_TOKEN,
    "lwa_app_id": SP_API_CLIENT_ID,
    "lwa_client_secret": SP_API_CLIENT_SECRET,
    "aws_secret_key": SP_API_SECRET_KEY,
    "aws_access_key": SP_API_ACCESS_KEY,
    "role_arn": SP_API_ROLE_ARN,
}


class AmazonAPI:
    def __init__(self):
        self.credentials = credentials
        self.products = Products(credentials=credentials, marketplace=Marketplaces.US)
        self.product_fees = ProductFees(
            credentials=credentials, marketplace=Marketplaces.US
        )

    def get_batch_product_details(self, asins, retries=0):
        try:
            response = self.products.get_competitive_pricing_for_asins(asin_list=asins)

            data = response.payload

            price_details = {}

            for product in data:
                try:
                    details = {}

                    # Add the asin to the details
                    asin = product["ASIN"]

                    product = product["Product"]

                    competitive_pricing = product.get("CompetitivePricing", {})
                    sales_rankings = product.get("SalesRankings", [{}])

                    # Get the offers that are new
                    offers = competitive_pricing.get("CompetitivePrices", [])
                    offers = [
                        offer for offer in offers if offer.get("condition") == "New"
                    ]

                    prices = [
                        offer.get("Price", {}).get("LandedPrice") for offer in offers
                    ]

                    if len(prices) != 0:
                        details["cost"] = (
                            min([price.get("Amount", 0) for price in prices])
                            if prices
                            else 0
                        )

                    try:
                        details["sales_rank"] = sales_rankings[0].get("Rank", 0)
                    except:
                        pass

                    try:
                        details["sub_sales_rank"] = sales_rankings[1].get("Rank", 0)
                    except:
                        pass

                    new_offers = competitive_pricing.get("NumberOfOfferListings", [])
                    for offer in new_offers:
                        if offer.get("condition") == "New":
                            details["offers"] = offer.get("Count", 0)
                            break

                    price_details[asin] = details
                except Exception as e:
                    print(e)
                    continue

            return price_details

        except Exception as e:
            if retries < 3:
                print(f"Retrying {retries}...")
                retries += 1
                sleep_time = int(3.0 * retries)
                print(e)
                time.sleep(sleep_time)
                return self.get_batch_product_details(asins, retries)

            print(e)
            return None

    def get_batch_fees(self, fees_dict: List[dict]):
        try:
            response = self.product_fees.get_product_fees_estimate(fees_dict)

            data = response.payload

            fees = {}

            for fee in data:
                try:
                    if fee.get("Status") != "Success":
                        continue

                    asin = fee.get("FeesEstimateIdentifier", {}).get("IdValue")
                    fee_details = fee.get("FeesEstimate").get("FeeDetailList")
                    referral_fee = 0
                    fba_fee = 0

                    for detail in fee_details:
                        if detail.get("FeeType") == "ReferralFee":
                            referral_fee = detail.get("FinalFee").get("Amount")
                        elif detail.get("FeeType") == "FBAFees":
                            fba_fee = detail.get("FinalFee").get("Amount")

                    fees[asin] = {"referral_fee": referral_fee, "fba_fee": fba_fee}

                except Exception as e:
                    print(e)
                    continue

            return fees

        except Exception as e:
            print(e)
            return None
