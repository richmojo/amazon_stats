from supabase import create_client
import os, time


def load_supabase():
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)


def get_asins():
    supabase = load_supabase()
    current_time = int(time.time())
    # 60 minutes
    threshold = current_time - (60 * 60)

    asins = (
        supabase.table("amazon_asins")
        .select("*")
        .lt("updated_at", threshold)
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
    response = supabase.rpc("sync_asins_from_sourcing", {}).execute()

    return
