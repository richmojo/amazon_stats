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


def sync_asins():
    supabase = load_supabase()
    batch_size = 100
    total_processed = 0

    while True:
        response = supabase.rpc(
            "sync_asins_from_sourcing_incremental", {"batch_size": batch_size}
        ).execute()
        processed_count = response.data
        total_processed += processed_count
        print(f"Processed: {processed_count}")

        if processed_count == 0:
            break  # No more unprocessed products

        time.sleep(1)

    print(f"Total processed: {total_processed}")
    return total_processed


# https://www.amazon.com/s?k=monitors&i=todays-deals&rh=p_36%3A4800-14000&ref=nb_sb_noss_1

# https://www.amazon.com/s?k=monitors&i=todays-deals&bbn=21101958011&rh=p_36%3A4800-14000&qid=1721939092&rnid=386442011&ref=sr_nr_p_36_0_0
