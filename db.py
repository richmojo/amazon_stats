from supabase import create_client
import os, time


def load_supabase():
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)


def get_asins():
    supabase = load_supabase()
    current_time = int(time.time())
    threshold = current_time - (60 * 60 * 24)

    asins = (
        supabase.table("amazon_asins")
        .select("*")
        .lt("updated_at", threshold)
        .order("updated_at", desc=False)
        .limit(1000)
        .execute()
    )

    if asins:
        return asins.data

    return []


def save_asins(data):
    supabase = load_supabase()
    updated_at = int(time.time())

    final_data = []
    updated_asins = []

    for row in data:
        asin = row["asin"]
        product_data = row["data"]
        fba_fee = product_data.get("fba_fee", 0)
        fba_fee = fba_fee if fba_fee else 0
        fba_fee = float(fba_fee)
        fba_fee = round(fba_fee, 2)

        referral_fee = product_data.get("referral_fee", 0)
        referral_fee = referral_fee if referral_fee else 0
        referral_fee = float(referral_fee)
        referral_fee = round(referral_fee, 2)

        variable_closing_fee = product_data.get("variable_closing_fee", 0)
        variable_closing_fee = variable_closing_fee if variable_closing_fee else 0
        variable_closing_fee = float(variable_closing_fee)
        variable_closing_fee = round(variable_closing_fee, 2)

        per_item_fee = product_data.get("per_item_fee", 0)
        per_item_fee = per_item_fee if per_item_fee else 0
        per_item_fee = float(per_item_fee)
        per_item_fee = round(per_item_fee, 2)

        offers = product_data.get("offers", 0)
        sales_rank = product_data.get("sales_rank", 0)
        sales_rank_category = product_data.get("sales_rank_category", "")
        sub_sales_rank = product_data.get("sub_sales_rank", 0)
        sub_sales_rank_category = product_data.get("sub_sales_rank_category", "")

        price = product_data.get("price", 0)
        fba_fee_percentage = fba_fee / price if price else 0
        fba_fee_percentage = round(fba_fee_percentage, 2)
        referral_fee_percentage = referral_fee / price if price else 0
        referral_fee_percentage = round(referral_fee_percentage, 2)

        final_data.append(
            {
                "asin": asin,
                "fba_fee": fba_fee,
                "fba_fee_percentage": fba_fee_percentage,
                "referral_fee": referral_fee,
                "referral_fee_percentage": referral_fee_percentage,
                "variable_closing_fee": variable_closing_fee,
                "per_item_fee": per_item_fee,
                "offers": offers,
                "sales_rank": sales_rank,
                "sales_rank_category": sales_rank_category,
                "sub_sales_rank": sub_sales_rank,
                "sub_sales_rank_category": sub_sales_rank_category,
                "price": price,
                "updated_at": updated_at,
            }
        )

        updated_asins.append({"asin": asin, "updated_at": updated_at})

    supabase.table("amazon_data").upsert(final_data).execute()
    supabase.table("amazon_asins").upsert(updated_asins).execute()


def merge_product_data_batch():
    supabase = load_supabase()
    response = supabase.rpc("update_batch_sourcing_products", {}).execute()

    if response:
        return response.data

    return False


def merge_a2a_product_data_batch():
    supabase = load_supabase()
    response = supabase.rpc("update_batch_a2a_products", {}).execute()

    if response:
        return response.data

    return False


def sync_asins():
    supabase = load_supabase()
    batch_size = 500
    total_processed = 0

    while True:
        # Process sourcing_products
        response_sourcing = supabase.rpc(
            "sync_asins_from_sourcing", {"batch_size": batch_size}
        ).execute()
        processed_count_sourcing = response_sourcing.data
        total_processed += processed_count_sourcing

        # Process a2a_products
        response_a2a = supabase.rpc(
            "sync_asins_from_a2a", {"batch_size": batch_size}
        ).execute()
        processed_count_a2a = response_a2a.data
        total_processed += processed_count_a2a

        # If nothing was processed from both, break the loop
        if processed_count_sourcing == 0 and processed_count_a2a == 0:
            break

        time.sleep(1)

    print(f"Total processed: {total_processed}")
    return total_processed


def delete_asins():
    supabase = load_supabase()
    batch_size = 50
    total_deleted = 0

    while True:
        response = supabase.rpc(
            "clean_asins_batch", {"batch_size": batch_size}
        ).execute()
        deleted_count = response.data
        total_deleted += deleted_count

        if deleted_count == 0:
            break

        time.sleep(1)

    print(f"Total deleted: {total_deleted}")
    return total_deleted
