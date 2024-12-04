from supabase import create_client
import os, time


def load_supabase():
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)


def get_asins():
    supabase = load_supabase()
    asins = []

    # First get non-a2a tasks
    non_a2a_asins = (
        supabase.table("amazon_asins")
        .select("asin")
        .eq("task_type", "non_a2a")
        .order("updated_at", desc=False)
        .limit(1000)
        .execute()
    )

    if non_a2a_asins and non_a2a_asins.data:
        asins.extend(non_a2a_asins.data)

    if len(asins) < 1000:
        a2a_asins = (
            supabase.table("amazon_asins")
            .select("asin")
            .eq("task_type", "a2a")
            .order("updated_at", desc=False)
            .limit(1000)
            .execute()
        )

        if a2a_asins and a2a_asins.data:
            asins.extend(a2a_asins.data)

    return asins


def save_asins(data):
    supabase = load_supabase()
    updated_at = int(time.time())

    final_data = []
    asins_to_delete = []

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

        asins_to_delete.append(asin)

    supabase.table("amazon_data").upsert(final_data).execute()
    supabase.table("amazon_asins").delete().in_("asin", asins_to_delete).execute()


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


def merge_reverse_sourcing_data_batch():
    supabase = load_supabase()
    response = supabase.rpc("update_batch_reverse_sourcing_products", {}).execute()

    if response:
        return response.data

    return False


def sync_asins():
    supabase = load_supabase()
    batch_size = 500
    total_processed = 0
    offset = 0
    a2a_done = False
    sourcing_done = False

    while True:
        if not sourcing_done:
            # Process sourcing_products
            response_sourcing = supabase.rpc(
                "sync_asins_from_sourcing",
                {"batch_size": batch_size, "batch_offset": offset},
            ).execute()

            # Get the counts for both found and processed
            found_count_sourcing = next(
                (
                    row["count"]
                    for row in response_sourcing.data
                    if row["operation_type"] == "ASINs found"
                ),
                0,
            )
            processed_count_sourcing = next(
                (
                    row["count"]
                    for row in response_sourcing.data
                    if row["operation_type"] == "ASINs inserted/updated"
                ),
                0,
            )
            total_processed += processed_count_sourcing

            # If no ASINs were found in sourcing_products, mark as done
            if found_count_sourcing == 0:
                print("Sourcing done")
                sourcing_done = True

        if not a2a_done:

            # Process a2a_products
            response_a2a = supabase.rpc(
                "sync_asins_from_a2a",
                {"batch_size": batch_size, "batch_offset": offset},
            ).execute()

            # Get the counts for both found and processed
            found_count_a2a = next(
                (
                    row["count"]
                    for row in response_a2a.data
                    if row["operation_type"] == "ASINs found"
                ),
                0,
            )
            processed_count_a2a = next(
                (
                    row["count"]
                    for row in response_a2a.data
                    if row["operation_type"] == "ASINs inserted/updated"
                ),
                0,
            )
            total_processed += processed_count_a2a

            # If no ASINs were found in a2a_products, mark as done
            if found_count_a2a == 0:
                print("A2A done")
                a2a_done = True

        # If no ASINs were found in both queries, break the loop
        if found_count_sourcing == 0 and found_count_a2a == 0:
            break

        # Increment offset for next batch
        offset += batch_size
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


raw_products = []
