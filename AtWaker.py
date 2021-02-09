import discord
import pandas as pd
import numpy as np
import os
from discord.ext import tasks
from datetime import datetime ,timedelta
# from dotenv import load_dotenv
import time
import asyncio
import r
import pickle

# .envファイルの内容を読み込みます
# load_dotenv()
TOKEN = os.environ['TOKEN']

intents = discord.Intents.all()
# 接続に必要なオブジェクトを生成
client = discord.Client(intents=intents)
# channelid=os.environ['CHANNEL']
# serverid=os.environ['SERVER']
# thisbotid=os.environ['THISBOT']
channelid=805226148195074089
serverid=805058528485965894
thisbotid=807869171491668020
print(client.get_channel(channelid))
z=86400*((365.25*50)//1+5/8)//1
hs=6
ms=0
interv=15
clen=360
hs=((time.time()+3600*9)%86400)//3600
ms=((time.time())%3600)//60+1
interv=0.25
clen=1
v=None
emj='<:ohayo:805676181328232448>'
contesting=0
rk=1
conn=r.connect()

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
    dbv=pd.read_csv('variables_'+str(serverid)+'.csv',header=0,index_col=0)
    v=pd.read_csv('v_'+str(serverid)+'.csv',header=0,index_col=0)
    global emj
    global contesting
    global rk
    emj=dbv.loc['emj','variables']
    contesting=int(dbv.loc['contesting','variables'])
    rk=int(dbv.loc['rk','variables'])
    return

def save_vars():
    vars=pd.DataFrame([[str(emj)],[rk],[contesting]],index=['emj','rk','contesting'],columns=['variables'])
    vars.to_csv('variables_'+str(serverid)+'.csv')
    v.to_csv('v_'+str(serverid)+'.csv')



def renew_db(serverid):
    guild=client.get_guild(serverid)
    db=get_cached_df('AtWaker_data_'+str(serverid))
    for xx in {str(aa.id) for aa in guild.members}-set(db.index.astype(str)):
        db[xx]=[np.nan for _ in range(len(db))]
    cache_df('AtWaker_data_'+str(serverid),db)
    dbr=get_cached_df('AtWaker_rate_'+str(serverid))
    for xx in {str(aa.id) for aa in guild.members}-set(dbr.index.astype(str)):
        dbr[xx]=[np.nan for _ in range(len(dbr))]
    cache_df('AtWaker_rate_'+str(serverid),dbr)
    
def make_db(serverid):
    guild=client.get_guild(serverid)
    db=pd.DataFrame(columns=[str(xx.id) for xx in guild.members],index=[])
    cache_df('AtWaker_data_'+str(serverid),db)
    dbr=pd.DataFrame(columns=[str(xx.id) for xx in guild.members],index=[])
    cache_df('AtWaker_rate_'+str(serverid),dbr)
    
# async def repeat1(start,msg):
#   while time.time()-start<60*(clen+1):
#     print('rep1s')
#     reaction, user = await client.wait_for('reaction_add', check=lambda r, u: 
#                                            (r.message.id==msg.id) and ((r.emoji==emj) or ((r.emoji==emj2) and (u.id==807869171491668020))))
#     print('rep1')
#     if r.emoji==emj:
#       v=record_rank(user,rk,v)
#       rk+=1
#     elif r.emoji==emj2:
#       break


# async def repeat2(msg):
#   await asyncio.sleep(60*clen)
#   print('rep2')
#   await msg.add_reaction(emoji=emj2)

    
async def contest():
    channel = client.get_channel(channelid)
    global v
    db=get_cached_df('AtWaker_data_'+str(serverid))
    v=pd.DataFrame([[np.nan,np.nan] for _ in range(len(db.columns))],columns=['rank','time'],index=db.columns)
    save_vars()
    dt=(datetime.now()+timedelta(hours=9)).strftime('%Y-%m-%d')
    global rk
    rk=1
    save_vars()
    start=time.time()
    msg=await channel.send('おはようございます！ Good morning!\n'+dt
                                                                                        +'のAtWaker Contest開始です。\n起きた人は'
                                                                                        +emj+'でリアクションしてね。')
    await msg.add_reaction(emoji=emj)
    global contesting
    contesting=1
    save_vars()
    print('Contest started')
    
    
async def contest_end():
    print('Contest ended')
    db=get_cached_df('AtWaker_data_'+str(serverid))
    channel = client.get_channel(channelid)
    dt=(datetime.now()+timedelta(hours=9)).strftime('%Y-%m-%d')
    global contesting
    contesting=0
    save_vars()
    if rk>1:
            await channel.send(dt+'のAtWaker Contestは終了しました。\n参加者は'
                                                                        +str(rk-1)+'人でした。')
            db.loc[dt]=[np.nan for _ in range(len(db.columns))]
            db=perf_calc(db,v)
            rate_calc(db,dt)
            vs=v.dropna().sort_values(by='rank')
            for j in range(1,min(11,rk)):
                jthuser=client.get_guild(serverid).get_member(int(vs.index[j-1]))
                await channel.send(str(j)+'位:'+jthuser.display_name+' '
                                                                                +vs.iloc[j-1].loc['time']+' パフォーマンス:'
                                                                                +str(int(db.loc[dt,vs.index[j-1]])))
    else:
        await channel.send('ほんでーかれこれまぁ'+str(clen)+'分くらい、えー待ったんですけども参加者は誰一人来ませんでした。')
    cache_df('AtWaker_data_'+str(serverid),db)
    return
    
def record_rank(user,rk,v):
    vc=v.copy()
    if vc.loc[str(user.id),'rank']!=vc.loc[str(user.id),'rank']:
        vc.loc[str(user.id),'time']=(datetime.now()+timedelta(hours=9)).strftime('%H:%M:%S')
        vc.loc[str(user.id),'rank']=rk
    return vc

def perf_calc(db,v):
    dbc=db.copy()
    vc=v['rank'].dropna().sort_values()
    print(vc)
    aperf=pd.Series([np.nan]*len(vc),index=vc.index)
    for user in vc.index:
        past=dbc[user].dropna().values[::-1]
        if(len(past)==0):
            aperf[user]=1200
        else:
            aperfnom=0
            aperfden=0
            for i in range(len(past)):
                aperfnom+=past[i]*(0.9**(i+1))
                aperfden+=0.9**(i+1)
            aperf[user]=aperfnom/aperfden
    xx=0
    s=np.sum(1/(1+6.0**((xx-aperf.values)/400)))
    print(list(1/(1+6.0**((xx-aperf.values)/400))))
    for j in range(len(vc))[::-1]:
        print(s)
        while s>=j+0.5:
            xx+=1
            s=np.sum(1/(1+6.0**((xx-aperf.values)/400)))
        dbc.iloc[-1].loc[vc.index[j]]=int(xx)
    if len(dbc)==1:
        dbc.iloc[-1]=((dbc.iloc[-1]-1200)*3)//2+1200
    return dbc

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
            dbr.loc[dt,xx]=int(rate+0.5)
    cache_df('AtWaker_rate_'+str(serverid),dbr)
    return






# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました。')
    channel = client.get_channel(channelid)
    if (get_cached_df('AtWaker_rate_'+str(serverid))!=None) and  (get_cached_df('AtWaker_data_'+str(serverid))!=None):
        renew_db(serverid)
    else:
        make_db(serverid)
    await channel.send('起動しました。')
    return

# リアクション受信時に動作する処理
@client.event
async def on_reaction_add(reaction,user):
    global v
    global rk
    if (contesting==1) and (user.id!=807869171491668020):
        dt=(datetime.now()+timedelta(hours=9)).strftime('%Y-%m-%d')
        bool1=(str(reaction.emoji)==str(emj))
        bool2=(reaction.message.author.id==807869171491668020) 
        bool3=(reaction.message.content=='おはようございます！ Good morning!\n'+dt+'のAtWaker Contest開始です。\n起きた人は'+emj+'でリアクションしてね。')
        print(bool1,bool2,bool3)
        if bool1 and bool2 and bool3:
            print(rk,user.display_name)
            v=record_rank(user,rk,v)
            rk+=1
            save_vars()
    return
    

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    # global serverid
    # global channelid
    # if not contesting:
        # serverid=message.channel.guild.id
        # channelid=message.channel.id
    channel = client.get_channel(channelid)
    if message.content.startswith("!atw ") and (message.author.id!=thisbotid):
        if message.content.startswith("!atw start "):
            global emj
            emj=message.content[11:]
            save_vars()
            print(emj)
            if (get_cached_df('AtWaker_rate_'+str(serverid))!=None) and  (get_cached_df('AtWaker_data_'+str(serverid))!=None):
                renew_db(serverid)
            else:
                make_db(serverid)
            await channel.send('起動しました。')
        elif (message.content=="!atw reset "+TOKEN) and (message.author.id==602203895464329216):
            conn.delete('AtWaker_rate_'+str(serverid))
            print("rate cache reset")
            conn.delete('AtWaker_data_'+str(serverid))
            print("data cache reset")
            make_db(serverid)
        elif message.content.startswith("!atw rating "):
            if (get_cached_df('AtWaker_rate_'+str(serverid))!=None) and  (get_cached_df('AtWaker_data_'+str(serverid))!=None):
                dbr=get_cached_df('AtWaker_rate_'+str(serverid))
                dbd=get_cached_df('AtWaker_data_'+str(serverid))
                num=0
                print(len(channel.guild.members))
                for xx in channel.guild.members:
                    if message.content[12:] in xx.display_name:
                        zant=""
                        num+=1
                        if len(dbr)>0:
                            rate=int(dbr.iloc[-1].loc[str(xx.id)])
                            if(len(dbd.loc[:,str(xx.id)].dropna())<14):
                                zant="(暫定)"
                        else:
                            rate=0
                        await channel.send(xx.display_name+':'+str(rate)+zant)
                if num==0:
                    await channel.send('ユーザーが見つかりません。')
            else:
                await channel.send('初めに!atw start (絵文字)を実行してください。')
        elif message.content=="!atw help":
            f = open('help.txt', 'r')
            helpstr = f.read()
            f.close()
            await channel.send(helpstr)
        else:
            await channel.send('そのコマンドは存在しません。')
    return 
        
@client.event
async def on_member_join(member):
    if not (serverid==None) and not (channelid==None):
        renew_db(serverid)
    return

@tasks.loop(seconds=60*interv)
async def loop():
    # 現在の時刻
    now=(time.time()+3600*9)%86400
    print(now)
    bool1l=(3600*hs+60*ms<=now<3600*hs+60*(ms+interv))
    bool2l= not (serverid==None)
    bool3l= not (channelid==None)
    bool4l= (contesting==0)
    dfd=get_cached_df('AtWaker_data_'+str(serverid))
    dfr=get_cached_df('AtWaker_rate_'+str(serverid))
    bool5l=isinstance(dfd, pd.DataFrame):
    bool6l=isinstance(dfr, pd.DataFrame):
    print(bool1l ,bool2l ,bool3l,bool4l,bool5l,bool6l)
    if bool1l and bool2l and bool3l and bool4l and bool5l and bool6l:
        await contest()
    elif(3600*hs+60*(ms+clen)<=now<3600*hs+60*(ms+interv+clen)) and (contesting==1):
        await contest_end()
    return

#変数読み込み
load_vars()

#ループ処理実行
loop.start()

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)  


