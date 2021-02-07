import discord
import pandas as pd
import numpy as np
import os
from discord.ext import tasks
from datetime import datetime 

# 自分のBotのアクセストークンに置き換えてください
TOKEN = 'ODA3ODY5MTcxNDkxNjY4MDIw.YB-Qyw.ug72aycHBOcB4Zw9Xx0hWWdxWYM'

# 接続に必要なオブジェクトを生成
client = discord.Client()
channelid=None
serverid=None
emj=':sun_with_face:'
z=86400*((365.25*50)//1+5/8)

def renew_db(serverid,message):
    db=pd.read_csv('AtWaker_data_'+str(serverid)+'.csv',header=0,index_col=0)
    for xx in set(message.guild.members)-set(db.index):
        db[xx.id]=[np.nan for _ in range(len(db))]
    db.to_csv('AtWaker_data_'+str(serverid)+'.csv')
    dbr=pd.read_csv('AtWaker_rate_'+str(serverid)+'.csv',header=0,index_col=0)
    for xx in set(message.guild.members)-set(db.index):
        db[xx.id]=[np.nan for _ in range(len(db))]
    dbr.to_csv('AtWaker_rate_'+str(serverid)+'.csv')
  
def make_db(serverid,message):
    db=pd.DataFrame(columns=[xx.id for xx in message.guild.members],index=[])
    db.to_csv('AtWaker_data_'+str(serverid)+'.csv')
    dbr=pd.DataFrame(columns=[xx.id for xx in message.guild.members],index=[])
    dbr.to_csv('AtWaker_rate_'+str(serverid)+'.csv')
  
def contest():
    db=pd.read_csv('AtWaker_data_'+serverid+'.csv',header=0,index_col=0)
    channel = client.get_channel(channelid)
    v=pd.DataFrame([[np.nan,np.nan] for _ in range(len(db.columns))],columns=['rank','time'],index=db.columns)
    dt=datetime.now().strftime('%Y-%m-%d')
    sleep(3600-time.time()%3600)
    rk=1
    start=time.time()
    msg=await client.send_message(channel,'おはようございます！ Good morning!\n'+dt
                                            +'のAtWaker Contest開始です。\n起きた人は'
                                            +emj+'でリアクションしてね。')
    await client.add_reaction(msg, emoji=emj)
    while time.time()-start<3600*6:
        reaction, user = await client.wait_for('reaction_add', check=lambda r, u: r==emj)
        v=record_rank(user,rk,v)
        rk+=1
    if rk>1:
        await client.send_message(channel,dt+'のAtWaker Contestは終了しました。\n参加者は'
                                    +str(rk-1)+'人でした。')
        db.loc[dt]=[np.nan for _ in range(len(db.columns))]
        db=perf_calc(db,v)
        rate_calc(db,dt)
        vs=v.dropna().sort_values(by='rank')
        for j in range(1,min(11,rk)):
            jthuser=client.get_guild(serverid).get_member(vs.index[j-1])
            await client.send_message(channel,str(j)+'位:'+jthuser.display_name+' '
                                        +vs.iloc[j-1].loc['time']+' パフォーマンス:'
                                        +db[dt][vs.index[j-1]])
    else:
        await client.send_message(channel,'ほんでーかれこれまぁ6時間くらい、えー待ったんですけども参加者は誰一人来ませんでした。')
    db.to_csv('AtWaker_data_'+str(serverid)+'.csv')
    return
  
def record_rank(user,rk,v):
    vc=v.copy()
    if vc.loc[user,'rank']!=v.loc[user,'rank']:
        vc.loc[user,'time']=datetime.now().strftime('%H:%M:%S')
        vc.loc[user,'rank']=rk
    return vc

def perf_calc(db,v):
    dbc=db.copy()
    vc=v['rank'].dropna().sort_values()
    aperf=pd.Series([np.nan],index=v.index)
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
    s=np.sum(1/(1+6**((xx-aperf.values)/400)))
    for j in range(len(vc)):
        while s<=j+0.5:
            xx+=1
            s=np.sum(1/(1+6.0**((xx-aperf.values)/400)))
        dbc.iloc[-1].loc[vc.index[j]]=xx
    if len(dbc)==1:
        dbc.iloc[-1]=((dbc.iloc[-1]-1200)*3)//2+1200
    return dbc

def rate_calc(db,dt):
    dbr=pd.read_csv('AtWaker_rate_'+serverid+'.csv',header=0,index_col=0)
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
            dbr.loc[dt,xx]=int(800*np.log(ratenom/rateden)/np.log(2))
    dbr.to_csv('AtWaker_rate_'+str(serverid)+'.csv')
    return






# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました。')

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    serverid=message.guild.id
    channelid=message.channel.id
    if message.content.startswith=="!atw ":
        if message.content.startswith=="!atw start ":
            emj=message.content[11:]
            if os.path.exists('AtWaker_data_'+str(serverid)+'.csv') 
            and os.path.exists('AtWaker_rate_'+str(serverid)+'.csv'):
                renew_db(serverid,message)
                loop.cancel()
                #ループ処理実行
                loop.start()
            else:
                make_db(serverid,message)
                loop.cancel()
                #ループ処理実行
                loop.start()
        elif message.content.startswith=="!atw rating ":
            dbr=pd.read_csv('AtWaker_rate_'+serverid+'.csv',header=0,index_col=0)
            channel = client.get_channel(channelid)
            for xx in message.guild.members:
                if message.content[12:] in xx.display_name:
                    if len(dbr)>0:
                        rate=dbr.iloc[-1].loc[xx.id]
                    else:
                        rate=0
                await client.send_message(channel,xx.display_name+':'+str(rate))    
        else:
            channel = client.get_channel(channelid)
            await client.send_message(channel,'そのコマンドは存在しません。')
    return
    
@client.event
async def on_member_join(member):
    if not (serverid==None) and not (channelid==None):
        renew_db(serverid,message)
        loop.cancel()
        #ループ処理実行
        loop.start()
    return

@tasks.loop(seconds=60)
async def loop():
    # 現在の時刻
    now=time.time()
    nowstr = datetime.now().strftime('%H:%M')
    if nowstr == '05:55':
        contest()
        




# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)