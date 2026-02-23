import pyarrow.parquet as pq

if __name__ == "__main__":
    listings = pq.read_metadata('data/clean/horses_listings_limpio.parquet')
    print("Listings Columns:", listings.schema.names)

    sessions = pq.read_metadata('data/clean/horses_sessions_info.parquet')
    print("Sessions Columns:", sessions.schema.names)
