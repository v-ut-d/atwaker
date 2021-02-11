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
channelid=int(os.environ['CHANNEL'])
# channelid=805226148195074089
serverid=int(os.environ['SERVER'])
thisbotid=int(os.environ['THISBOT'])
print(client.get_channel(channelid))
z=86400*((365.25*50)//1+5/8)//1
hs=6
ms=0
interv=1
clen=360
msg_raz=6
# hs=((time.time()+3600*9)%86400)//3600
# ms=((time.time())%3600)//60+1
# interv=0.25
# clen=5
# msg_raz=5
v=None
emj='<:ohayo:805676181328232448>'
contesting=0
num_ra=0
min_display=20
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
    dbv=get_cached_df('variables_'+str(serverid))
    v=get_cached_df('v_'+str(serverid))
    global emj
    global contesting
    global num_ra
    emj=dbv.loc['emj','variables']
    contesting=int(dbv.loc['contesting','variables'])
    num_ra=int(dbv.loc['num_ra','variables'])
    return

def save_vars():
    vars=pd.DataFrame([[str(emj)],[num_ra],[contesting]],index=['emj','num_ra','contesting'],columns=['variables'])
    cache_df("variables_"+str(serverid),vars)
    cache_df("v_"+str(serverid),v)

def renew_db(serverid):
    guild=client.get_guild(serverid)
    db=get_cached_df('AtWaker_data_'+str(serverid))
    for xx in {str(aa.id) for aa in guild.members}-set(db.columns.astype(str)):
        db[xx]=[np.nan for _ in range(len(db))]
    cache_df('AtWaker_data_'+str(serverid),db)
    dbr=get_cached_df('AtWaker_rate_'+str(serverid))
    for xx in {str(aa.id) for aa in guild.members}-set(dbr.columns.astype(str)):
        dbr[xx]=[0 for _ in range(len(dbr))]
    cache_df('AtWaker_rate_'+str(serverid),dbr)
    print("df renewed")
    
def make_db(serverid):
    guild=client.get_guild(serverid)
    db=pd.DataFrame(columns=[str(xx.id) for xx in guild.members],index=[])
    cache_df('AtWaker_data_'+str(serverid),db)
    dbr=pd.DataFrame(columns=[str(xx.id) for xx in guild.members],index=[])
    cache_df('AtWaker_rate_'+str(serverid),dbr)
    print("df made")

# async def repeat1(start,msg):
#   while time.time()-start<60*(clen+1):
#     print('rep1s')
#     reaction, user = await client.wait_for('reaction_add', check=lambda r, u: 
#                                            (r.message.id==msg.id) and ((r.emoji==emj) or ((r.emoji==emj2) and (u.id==807869171491668020))))
#     print('rep1')
#     if r.emoji==emj:
#       v=record_rank(user,num_ra,v)
#       num_ra+=1
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
    v=pd.DataFrame(columns=['rank','time']+[str(i) for i in range(msg_raz)]+['total'],index=[])
    save_vars()
    dt=(datetime.now()+timedelta(hours=9)).strftime('%Y-%m-%d')
    global num_ra
    num_ra=0
    save_vars()
    start=time.time()
    msg=await channel.send('おはようございます！ Good morning!\n'+dt
                            +'のAtWaker Contest開始です。\n起きた人は下の「'+dt+' 〇回目」の\nメッセージに'
                            +emj+'でリアクションしてね。')
    global contesting
    contesting=1
    save_vars()
    await contest_msg(0)
    print('Contest started')
    return
    
async def contest_msg(i):
    channel = client.get_channel(channelid)
    dt=(datetime.now()+timedelta(hours=9)).strftime('%Y-%m-%d')
    msg=await channel.send(dt+' '+str(i+1)+'回目')    
    await msg.add_reaction(emoji=emj)
    return
    
async def contest_end():
    print('Contest ended')
    db=get_cached_df('AtWaker_data_'+str(serverid))
    channel = client.get_channel(channelid)
    dt=(datetime.now()+timedelta(hours=9)).strftime('%Y-%m-%d')
    global contesting
    contesting=0
    save_vars()
    if num_ra>0:
            await channel.send(dt+'のAtWaker Contestは終了しました。\n参加者は'
                                                                        +str(len(v.dropna()))+'人でした。')
            db.loc[dt]=[np.nan for _ in range(len(db.columns))]
            perf_calc(db)
            db=get_cached_df('AtWaker_data_'+str(serverid))
            rate_calc(db,dt)
            vs=v.dropna().sort_values(by='rank')
            for j in range(1,min(min_display+1,len(vs)+1)):
                jthuser=client.get_guild(serverid).get_member(int(vs.index[j-1]))
                await channel.send(str(j)+'位:'+jthuser.display_name+' '
                                    +vs.iloc[j-1].loc['time']+' パフォーマンス:'
                                    +str((int(db.loc[dt,vs.index[j-1]]) if isinstance(db.loc[dt,vs.index[j-1]],int) else db.loc[dt,vs.index[j-1]])))
    else:
        await channel.send('ほんでーかれこれまぁ'+str(clen)+'分くらい、えー待ったんですけども参加者は誰一人来ませんでした。')

    return
    

def record_rank(user,i):
    global v
    vc=v.copy()
    if not (str(user.id) in vc.index):
        vc.loc[str(user.id)]=[0]*len(vc.columns)
        vc.loc[str(user.id),'time']=(datetime.now()+timedelta(hours=9)).strftime('%H:%M:%S')
    if  vc.loc[str(user.id),str(i)]==0:
        vc.loc[str(user.id),str(i)]=(3600*(hs-9)+60*(ms+clen)+86400-time.time()%86400)%86400
    v=vc
    save_vars()
    return 

def perf_calc(db):
    dbc=db.copy()
    global v
    v['total']=np.sum(v[[str(i) for i in range(msg_raz)]].values,axis=1)
    v=v.sort_values(by='total',ascending=False)
    v['rank']=list(range(1,len(v)+1))
    save_vars()
    vc=v['rank']
    print(v)
    aperf=pd.Series([np.nan]*len(vc),index=vc.index)
    for user in vc.index:
        user=str(user)
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
    xx=-int(800*np.log(len(vc))/np.log(6))
    s=np.sum(1/(1+6.0**((xx-aperf.values)/400)))
    print(list(1/(1+6.0**((xx-aperf.values)/400))))
    for j in range(len(vc))[::-1]:
        print(s)
        while s>=j+0.5:
            xx+=1
            s=np.sum(1/(1+6.0**((xx-aperf.values)/400)))
        dbc.iloc[-1].loc[vc.index[j]]=int(xx)
    if len(dbc)==1:
        dbc.iloc[-1]=((dbc.iloc[-1].values-1200)*3)//2+1200
    for j in range(len(vc))[::-1]:
        if dbc.iloc[-1].loc[vc.index[j]]<=400:
            dbc.iloc[-1].loc[vc.index[j]]=int(400*np.e**(dbc.iloc[-1].loc[vc.index[j]]/400-1))
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
            dbr.loc[dt,xx]=int(rate+0.5)
    cache_df('AtWaker_rate_'+str(serverid),dbr)
    return






# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました。')
    channel = client.get_channel(channelid)
    if isinstance(get_cached_df('AtWaker_rate_'+str(serverid)),pd.DataFrame) and  isinstance(get_cached_df('AtWaker_data_'+str(serverid)),pd.DataFrame):
        renew_db(serverid)
    else:
        make_db(serverid)
    await channel.send('起動しました。')
    return

# リアクション受信時に動作する処理
@client.event
async def on_reaction_add(reaction,user):
    global v
    global num_ra
    if (contesting==1) and (user.id!=807869171491668020):
        dt=(datetime.now()+timedelta(hours=9)).strftime('%Y-%m-%d')
        for i in range(msg_raz):
            bool1=(str(reaction.emoji)==str(emj))
            bool2=(reaction.message.author.id==807869171491668020) 
            # bool3=(reaction.message.content=='おはようございます！ Good morning!\n'+dt+'のAtWaker Contest開始です。\n起きた人は'+emj+'でリアクションしてね。')
            bool3=(reaction.message.content==dt+' '+str(i+1)+'回目')
            print(bool1,bool2,bool3)
            if bool1 and bool2 and bool3:
                print(num_ra,user.display_name)
                num_ra+=1
                record_rank(user,i)
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
    guild=client.get_guild(serverid)
    if message.content.startswith("!atw ") and (message.author.id!=thisbotid):
        if message.content.startswith("!atw start "):
            global emj
            emj=message.content[11:]
            save_vars()
            print(emj)
            if isinstance(get_cached_df('AtWaker_rate_'+str(serverid)),pd.DataFrame) and  isinstance(get_cached_df('AtWaker_data_'+str(serverid)),pd.DataFrame):
                renew_db(serverid)
            else:
                make_db(serverid)
            await channel.send('起動しました。')
        elif (message.content.startswith("!atw reset ")) and (message.author.id==602203895464329216):
            if message.content[11:]=='all':
                conn.delete('AtWaker_rate_'+str(serverid))
                print("rate cache reset")
                conn.delete('AtWaker_data_'+str(serverid))
                print("data cache reset")
                make_db(serverid)
                await channel.send('データを全て消去しました。')
            else:
                try:
                    dbr=get_cached_df('AtWaker_rate_'+str(serverid))
                    dbd=get_cached_df('AtWaker_data_'+str(serverid))
                    dbr.drop(message.content[11:],axis=0)
                    dbd.drop(message.content[11:],axis=0)
                    cache_df('AtWaker_rate_'+str(serverid),dbr)
                    cache_df('AtWaker_data_'+str(serverid),dbd)
                    await channel.send(message.content[11:]+'のデータを消去しました。')
                except:
                    await channel.send('引数が不正です。')
        elif message.content.startswith("!atw rating "):
            if isinstance(get_cached_df('AtWaker_rate_'+str(serverid)),pd.DataFrame) and  isinstance(get_cached_df('AtWaker_data_'+str(serverid)),pd.DataFrame):
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
                            zant="(未参加)"
                        await channel.send(xx.display_name+':'+str(rate)+zant)
                if num==0:
                    await channel.send('ユーザーが見つかりません。')
            else:
                await channel.send('初めに!atw start (絵文字)を実行してください。')
        elif  message.content.startswith("!atw rating-ranking "):
            if isinstance(get_cached_df('AtWaker_rate_'+str(serverid)),pd.DataFrame):
                dbr=get_cached_df('AtWaker_rate_'+str(serverid))
                dbd=get_cached_df('AtWaker_data_'+str(serverid))
                if len(dbr)>0:
                    try:
                        z=max(int(message.content[20:]),1)
                        for rk in range(z-1,min(z-1+min_display,len(dbr.iloc[-1]))):
                            rate=str(int(dbr.iloc[-1].sort_values(ascending=False).iloc[rk]))
                            userid=int(dbr.iloc[-1].sort_values(ascending=False).index[rk])
                            zant=""
                            if guild.get_member(userid)==None:
                                username='[deleted]'
                            else:
                                username=guild.get_member(userid).display_name
                            if len(dbd[str(userid)].dropna())==0:
                                zant="(未参加)"
                            elif len(dbd[str(userid)].dropna())<14:
                                zant="(暫定)"
                            await channel.send(str(rk+1)+'位:'+username+' '+rate+zant)
                    except Exception as e:
                        print(e)
                        await channel.send('引数が不正です。')
                else:
                    await channel.send('まだコンテストが開催されていません。')
            else:
                await channel.send('初めに!atw start (絵文字)を実行してください。')
        elif  message.content.startswith("!atw perf-ranking "):
            if isinstance(get_cached_df('AtWaker_data_'+str(serverid)),pd.DataFrame):
                dbd=get_cached_df('AtWaker_data_'+str(serverid))
                try:
                    a,b=message.content[18:].split()
                    z=max(int(b),1)
                    for rk in range(z-1,min(z-1+min_display,len(dbd.loc[a].dropna()))):
                        perf=str(int(dbd.loc[a].dropna().sort_values(ascending=False).iloc[rk]))
                        userid=int(dbd.loc[a].dropna().sort_values(ascending=False).index[rk])
                        if guild.get_member(userid)==None:
                            username='[deleted]'
                        else:
                            username=guild.get_member(userid).display_name
                        await channel.send(str(rk+1)+'位:'+username+' '+perf)
                except Exception as e:
                    print(e)
                    await channel.send('引数が不正です。')
            else:
                await channel.send('初めに!atw start (絵文字)を実行してください。')
        elif message.content=="!atw help":
            f = open('help.txt', 'r')
            helpstr = f.read()
            f.close()
            await channel.send(helpstr)
        elif (message.content=="!atw contest_end") and (message.author.id==602203895464329216):
            global num_ra
            num_ra=1
            await contest_end()
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
    bool5l=isinstance(dfd, pd.DataFrame)
    bool6l=isinstance(dfr, pd.DataFrame)
    print(bool1l ,bool2l ,bool3l,bool4l,bool5l,bool6l)
    if bool1l and bool2l and bool3l and bool4l and bool5l and bool6l:
        await contest()
    elif(3600*hs+60*(ms+clen)<=now<3600*hs+60*(ms+interv+clen)) and (not bool4l):
        await contest_end()
    else:
        for i in range(1,msg_raz):
            if (3600*hs+60*(ms+clen*i/msg_raz)<=now<3600*hs+60*(ms+interv+clen*i/msg_raz)) and (not bool4l) and bool5l and bool6l:
                await contest_msg(i)
    
    return

#変数読み込み
if isinstance(get_cached_df('v_'+str(serverid)),pd.DataFrame) and isinstance(get_cached_df('variables_'+str(serverid)),pd.DataFrame):
    load_vars()
else:
    v=pd.read_csv('v_'+str(serverid)+'.csv',header=0,index_col=0)
    dbv=pd.read_csv('variables_'+str(serverid)+'.csv',header=0,index_col=0)
    emj=dbv.loc['emj','variables']
    contesting=int(dbv.loc['contesting','variables'])
    num_ra=int(dbv.loc['num_ra','variables'])

#ループ処理実行
loop.start()

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)  


