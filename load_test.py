import pandas as pd
import time
import os
import psutil

process = psutil.Process(os.getpid())

def mem():
    return f"{process.memory_info().rss / 1024 / 1024:.2f} MB"

data_dir = os.path.join("data", "clean")

print(f"[{mem()}] Starting test...")

t0 = time.time()
print(f"[{mem()}] Loading horses...")
df1 = pd.read_parquet(os.path.join(data_dir, "horses_listings_limpio.parquet"))
print(f"[{mem()}] Horses loaded: {len(df1)} rows in {time.time()-t0:.2f}s")

t1 = time.time()
print(f"[{mem()}] Loading products...")
df2 = pd.read_parquet(os.path.join(data_dir, "products_listing_limpio.parquet"))
print(f"[{mem()}] Products loaded: {len(df2)} rows in {time.time()-t1:.2f}s")

u_cols = ['event_time', 'event_type', 'horse_id']
t2 = time.time()
print(f"[{mem()}] Loading horse sessions (Specific Cols)...")
df3 = pd.read_parquet(os.path.join(data_dir, "horses_sessions_info.parquet"), engine='fastparquet')
print(f"[{mem()}] Horse Sessions loaded: {len(df3)} rows in {time.time()-t2:.2f}s")
