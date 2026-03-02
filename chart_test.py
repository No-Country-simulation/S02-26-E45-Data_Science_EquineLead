import pandas as pd
import time
import os

data_dir = os.path.join("data", "clean")

print("Starting chart agg tests...")

u_cols = ['event_time', 'event_type', 'horse_id']
p_cols = ['event_time', 'event_type', 'item_id']

t0=time.time()
df_u_sessions = pd.read_parquet(os.path.join(data_dir, "horses_sessions_info.parquet"), columns=u_cols, engine='fastparquet')
df_u_sessions = df_u_sessions.sample(n=min(10000, len(df_u_sessions)), random_state=42)

df_p_sessions = pd.read_parquet(os.path.join(data_dir, "prods_sessions_info.parquet"), columns=p_cols, engine='fastparquet')
df_p_sessions = df_p_sessions.sample(n=min(10000, len(df_p_sessions)), random_state=42)
print("Load complete:", time.time()-t0)

t1=time.time()
df_u_sessions['date'] = pd.to_datetime(df_u_sessions['event_time'], errors='coerce').dt.date
h_ev = df_u_sessions.groupby('date').size().reset_index(name='Horse')
df_p_sessions['date'] = pd.to_datetime(df_p_sessions['event_time'], errors='coerce').dt.date
p_ev = df_p_sessions.groupby('date').size().reset_index(name='Product')
merged_ev = pd.merge(h_ev, p_ev, on='date', how='outer').fillna(0).sort_values('date')
print("Exec Summary Aggs:", time.time()-t1)

t2=time.time()
htime = df_u_sessions.groupby(['date', 'event_type']).size().reset_index(name='Count')
ptime = df_p_sessions.groupby(['date', 'event_type']).size().reset_index(name='Count')
print("Funnel Time Aggs:", time.time()-t2)

print("ALL CLEAR.")
