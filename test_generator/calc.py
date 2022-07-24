import pandas as pd
import numpy as np


def perf_calc(dbc:pd.DataFrame,v:pd.DataFrame,dt:str,msg_raz:int,clen:int):
    # calculate total and rank in v
    v['total']=np.sum(v[[str(i) for i in range(msg_raz)]].values,axis=1)
    if 86400-max(v['total'].values)<=60:
        v['total']=(v['total']+60)%86400
    v=v.sort_values(by='total',ascending=False)
    v['rank']=((max(v['total'].values)-v['total'].values)/(60*clen*(msg_raz+1)/2))*(len(v)-1)
    vc=v['rank']
    # print(v)
    # print(vc)

    # calculate aperf(inner rate)
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
    aperf=aperf.sort_values(ascending=False)

    # calculate inner perf
    xx=-int(800*np.log(len(vc))/np.log(6))
    r0=np.array([0]+list(vc.values))
    rdiff=r0[1:]-r0[:-1]
    r1=r0[1:]-rdiff[0]/2+max(0,1/60/clen*len(vc)-rdiff[0])
    rdiff[0]=max(1/60/clen*len(vc),rdiff[0])
    s=np.sum(rdiff/(1+6.0**((xx-aperf.values)/400)))
    # print(list(1/(1+6.0**((xx-aperf.values)/400))))
    for j in range(len(vc))[::-1]:
        # print(xx,s)
        while s>r1[j]:
            xx+=1
            s=np.sum(rdiff/(1+6.0**((xx-aperf.values)/400)))
        dbc.at[dbc.index[-1],vc.index[j]]=int(xx)
    
    # adjust performance at the first contest
    if len(dbc)==1:
        dbc.iloc[-1]=((dbc.iloc[-1].values-1200)*3)//2+1200
    
    # unknown
    perfave=dbc.iloc[-1].dropna().mean()
    perfstd=dbc.iloc[-1].dropna().std(ddof=0)
    correctionave=1200+300*np.log(len(dbc.iloc[-1].dropna()))
    correctionstd=800*np.log(6.0)
    dbc.iloc[-1]+=correctionave-perfave
    if len(dbc.iloc[-1].dropna())>1:
        dbc.iloc[-1]=correctionave+(dbc.iloc[-1]-correctionave)*correctionstd/perfstd

    # beginner correction
    for j in range(len(vc))[::-1]:
        if dbc.at[dt,vc.index[j]]<=400:
            dbc.at[dt,vc.index[j]]=int(400*np.e**(dbc.iloc[-1].loc[vc.index[j]]/400-1))
        elif dbc.at[dt,vc.index[j]]*0==0:
            dbc.at[dt,vc.index[j]]=int(dbc.iloc[-1].loc[vc.index[j]])
    
    return 

def rate_calc(db:pd.DataFrame,dbr:pd.DataFrame,dt:str):
    I=1000
    N=100
    L=np.log(N)/np.log(100)
    R=(15*10**12+490153)**(10/N)/10**(140/N)
    S=I/sum([np.log(101-(N-i)**(1/L))*R**(i+1) for i in range(N)])*sum([R**(i+1) for i in range(N)])
    print(R,S)
    if len(dbr)>0:
        vlast=dbr.iloc[-1]
        dbr.loc[dt]=vlast
        timelapse=0.99**((np.datetime64(dt)-np.array(db.index,dtype="datetime64"))//np.timedelta64(1,"D"))
    else:
        dbr.loc[dt]=[0]*len(dbr.columns)
        timelapse=np.array([1])
    for xx in db.columns:
        vperf=np.array((db[xx].values*timelapse)[::-1],dtype=float)
        vperf=vperf[np.logical_not(np.isnan(vperf))]
        vperfext=np.array(sorted([vperf[i//N]-S*np.log(101-(N-i%N)**(1/L)) for i in range(len(vperf)*N)])[::-1])
        print(vperfext[:N])
        ratenom=0
        rateden=0
        if len(vperfext)>=N:
            for i in range(N):
                ratenom+=vperfext[i]*(R**(i+1))
                rateden+=R**(i+1)
            rate=ratenom/rateden
            if rate<=400:
                rate=400*np.e**(rate/400-1)
            dbr.at[dt,xx]=int(rate+0.5)
        else:
            dbr.at[dt,xx]=0
    return