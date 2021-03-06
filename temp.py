import redis
import discord
import pandas as pd
import numpy as np
import os
from discord.ext import tasks
from datetime import datetime ,timedelta
# from dotenv import load_dotenv
import time
import asyncio
import pickle

def connect():
    return redis.from_url(
        url='redis://:p471a3b73197243c74de4d265d3687a498a94e7c3c4954ffa20f961e3c57cbc25@ec2-52-0-2-2.compute-1.amazonaws.com:12199', # 環境変数にあるURLを渡す
        # decode_responses=True, # 日本語の文字化け対策のため必須
    )

z=86400*((365.25*50)//1+5/8)//1
hs=7
ms=30
interv=1
clen=270
msg_raz=1
# hs=((time.time()+3600*9)%86400)//3600
# ms=((time.time())%3600)//60+1
# interv=0.25
# clen=5
# msg_raz=5
emj='<:ohayo:805676181328232448>'
contesting=0
num_ra=0
serverid=805058528485965894
msg_id=809914450052251648
conn=connect()

def cache_df(alias,df):
    df_compressed = pickle.dumps(df)
    res = conn.set(alias,df_compressed)
    if res == True:
        print('df cached')

def get_cached_df(alias):
    data = conn.get(alias)
    try:
        return pickle.loads(data)
    except:
        print("No data")
        return None



def load_vars():
    global v
    dbv=get_cached_df('variables_'+str(serverid))
    v=get_cached_df('v_'+str(serverid))
    global emj
    global contesting
    global num_ra
    global msg_id
    if 'emj' in dbv.index:
        emj=dbv.loc['emj','variables']
    if 'contesting' in dbv.index:
        contesting=int(dbv.loc['contesting','variables'])
    if 'num_ra' in dbv.index:
        num_ra=int(dbv.loc['num_ra','variables'])
    if 'msg_id' in dbv.index:
        msg_id=int(dbv.loc['msg_id','variables'])
    return

def save_vars():
    vars=pd.DataFrame([[str(emj)],[num_ra],[contesting],[msg_id]],index=['emj','num_ra','contesting','msg_id'],columns=['variables'])
    cache_df("variables_"+str(serverid),vars)
    cache_df("v_"+str(serverid),v)

load_vars()

v.loc['564310525715021835']=[1,'07:30:52',16148,0]
v.loc['351001323920949249']=[2,'07:31:15',16125,0]
v.loc['805053220325425172']=[3,'07:32:03',16077,0]
v.loc['242660319011405824']=[4,'07:38:13',15707,0]
v.loc['602203895464329216']=[5,'07:44:22',15338,0]
v.loc['805354010252017695']=[6,'07:52:14',14866,0]
v.loc['706391069599727657']=[7,'07:58:01',14519,0]
v.loc['581807612861874207']=[8,'08:01:13',14327,0]
v.loc['762947104490258462']=[9,'08:01:40',14300,0]
v.loc['698529378027569235']=[10,'08:01:50',14299,0]
v.loc['805344121186418689']=[11,'08:02:00',14280,0]
v.loc['794496518127747074']=[12,'08:03:09',14211,0]
v.loc['686197652328546428']=[13,'08:07:51',13929,0]
v.loc['535453638072729600']=[14,'08:15:41',13459,0]
print(v)
num_ra=14

save_vars()

# db=get_cached_df("AtWaker_data_"+str(serverid))
# dt=(datetime.now()+timedelta(hours=9)).strftime('%Y-%m-%d')
# dbr=get_cached_df("AtWaker_rate_"+str(serverid))
# if dt in db.index:
#     db=db.drop(dt, axis=0)
# if dt in dbr.index:
#     dbr=dbr.drop(dt,axis=0)
# cache_df("AtWaker_rate_"+str(serverid),dbr)

def perf_calc(db):
    dbc=db.copy()
    global v
    dt=(datetime.now()+timedelta(hours=9)).strftime('%Y-%m-%d')
    dbc.loc[dt]=[np.nan]*len(dbc.columns)
    v['total']=np.sum(v[[str(i) for i in range(msg_raz)]].values,axis=1)
    v=v.sort_values(by='total',ascending=False)
    v['rank']=list(range(1,len(v)+1))
    save_vars()
    vc=v['rank']
    print(v)
    print(vc)
    aperf=pd.Series([np.nan]*len(vc),index=vc.index)
    for user in vc.index:
        user=str(user)
        past=dbc[user].dropna().values[::-1]
        if(len(past)==0):
            aperf.at[user]=1200
        else:
            aperfnom=0
            aperfden=0
            for i in range(len(past)):
                aperfnom+=past[i]*(0.9**(i+1))
                aperfden+=0.9**(i+1)
            aperf.at[user]=aperfnom/aperfden
    xx=-int(800*np.log(len(vc))/np.log(6))
    s=np.sum(1/(1+6.0**((xx-aperf.values)/400)))
    print(list(1/(1+6.0**((xx-aperf.values)/400))))
    for j in range(len(vc))[::-1]:
        print(s)
        while s>=j+0.5:
            xx+=1
            s=np.sum(1/(1+6.0**((xx-aperf.values)/400)))
        dbc.at[dt,vc.index[j]]=int(xx)
    if len(dbc)==1:
        dbc.loc[dt]=((dbc.iloc[-1].values-1200)*3)//2+1200
    for j in range(len(vc))[::-1]:
        if dbc.at[dt,vc.index[j]]<=400:
            dbc.at[dt,vc.index[j]]=int(400*np.e**(dbc.iloc[-1].loc[vc.index[j]]/400-1))
    cache_df('AtWaker_data_'+str(serverid),dbc)
    return 

def rate_calc(db,dt):
    dbr=get_cached_df('AtWaker_rate_'+str(serverid))
    if len(dbr)>0:
        vlast=dbr.iloc[-1]
        dbr.loc[dt]=vlast
    else:
        dbr.loc[dt]=[0]*len(dbr.columns)
    for xx in db.columns:
        if db.loc[dt,xx]==db.loc[dt,xx]:
            vperf=db[xx].dropna().values[::-1]
            ratenom=0
            rateden=0
            for i in range(len(vperf)):
                ratenom+=2.0**(vperf[i]/800)*(0.9**(i+1))
                rateden+=0.9**(i+1)
            raz=len(vperf)
            corr=((1-0.81**raz)**0.5/(1-0.9**raz)-1)/(19**0.5-1)*1200
            rate=800*np.log(ratenom/rateden)/np.log(2)-corr
            if rate<=400:
                rate=400*np.e**(rate/400-1)
            dbr.at[dt,xx]=int(rate+0.5)
    cache_df('AtWaker_rate_'+str(serverid),dbr)
    return

# perf_calc(db)
# db=get_cached_df("AtWaker_data_"+str(serverid))
# rate_calc(db,dt)
# print(get_cached_df("AtWaker_data_"+str(serverid)).T.dropna(axis=0,how="all").sort_values(by=dt).head(40))
# print(get_cached_df("AtWaker_rate_"+str(serverid)).T.sort_values(by=dt,ascending=False).head(40))