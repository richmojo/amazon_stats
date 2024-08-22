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

    for row in data:
        row["updated_at"] = updated_at

    supabase.table("amazon_asins").upsert(data).execute()


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
    batch_size = 100
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


# https://www.amazon.com/s?k=monitors&i=todays-deals&rh=p_36%3A4800-14000&ref=nb_sb_noss_1

# https://www.amazon.com/s?k=monitors&i=todays-deals&bbn=21101958011&rh=p_36%3A4800-14000&qid=1721939092&rnid=386442011&ref=sr_nr_p_36_0_0
