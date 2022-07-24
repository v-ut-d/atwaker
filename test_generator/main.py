import os
from random import randrange

from calc import perf_calc, rate_calc
from variables import init_db, init_dbr, init_v, record_rank_to_v, renew_db

import pandas as pd
from datetime import datetime, timedelta, timezone

import numpy as np

TODAY = datetime(2022, 7, 21, 0, 0, 0, tzinfo=timezone.utc)


def simulate_contest(perf_db: pd.DataFrame, rate_db: pd.DataFrame, user_ids: list[str], msg_raz: int, dt: str):
    HS = 7
    MS = 30
    CLEN = 270

    num_ra = 0

    v = init_v(msg_raz)

    time_base = TODAY+timedelta(hours=HS-9, minutes=MS)
    # print(time_base, time_base.timestamp())
    for user_id in user_ids:
        now = time_base+timedelta(seconds=randrange(1, 60*CLEN))
        num_ra += record_rank_to_v(v, user_id, now, msg_raz, HS, MS, CLEN)

    perf_db.loc[dt] = [np.nan for _ in range(len(perf_db.columns))]
    perf_calc(perf_db, v, dt, msg_raz, CLEN)
    # rate_calc(perf_db, rate_db, dt)

    return v


def simulate_contests(days: int, max_users: int):
    v_list = []
    perf_db = init_db()
    rate_db = init_dbr()
    user_ids = ['user_'+str(i) for i in range(max_users)]
    renew_db(perf_db, rate_db, user_ids)
    for i in range(days):
        dt = (TODAY+timedelta(days=i, hours=9)).strftime('%Y-%m-%d')
        v = simulate_contest(perf_db, rate_db, user_ids, 1, dt)
        v_list.append(v)
    return (perf_db, rate_db, v_list)


perf_db, rate_db, v_list = simulate_contests(10, 10)
print('\nSimulation finished. Generating tables...')
if not os.path.exists('data'):
    os.makedirs('data')
for i, v in enumerate(v_list):
    v['time'].to_csv('data/in_'+str(i)+'.csv')
perf_db.to_csv('data/out_performance.csv')
rate_db.to_csv('data/out_rating.csv')
print('Tables generated.')