import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def init_v(msg_raz: int):
    # 行がユーザーに対応
    return pd.DataFrame(columns=['rank', 'time']+[str(i) for i in range(msg_raz)]+['total'], index=[])


def record_rank_to_v(v: pd.DataFrame, user_id: str, now: datetime, msg_raz: int, hs: int, ms: int, clen: int):
    ranks_increment = 0
    if not (str(user_id) in v.index):
        v.loc[str(user_id)] = [0]*len(v.columns)
        v.at[str(user_id), 'time'] = (now +
                                      timedelta(hours=9)).strftime('%H:%M:%S.%f')
    for i in range(msg_raz):
        if v.loc[str(user_id), str(i)] == 0:
            ranks_increment += 1
            v.at[str(user_id), str(i)] = (3600*(hs-9)+60 *
                                          (ms+clen)+86460-now.timestamp() % 86400) % 86400
    return ranks_increment  # incremental of num_ra


def init_db():
    # 行がコンテストに, 列がユーザーに対応。パフォーマンスを格納している。
    db = pd.DataFrame(columns=['dummy'])
    db.loc['1970-01-01'] = [np.nan]
    return db


def init_dbr():
    # 行がコンテストに, 列がユーザーに対応。レートを格納している。
    return pd.DataFrame()


def renew_db(db: pd.DataFrame, dbr: pd.DataFrame, user_ids: list[str]):
    for xx in set(user_ids)-set(db.columns.astype(str)):
        db[xx] = [np.nan for _ in range(len(db))]
    for xx in set(user_ids)-set(dbr.columns.astype(str)):
        dbr[xx] = [0 for _ in range(len(dbr))]
