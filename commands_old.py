# メッセージ受信時に動作する処理

# @client.event
# async def on_message(message):
#     # global serverid
#     # global channelid
#     # if not contesting:
#         # serverid=message.channel.guild.id
#         # channelid=message.channel.id
#     channel = message.channel
#     guild=client.get_guild(serverid)
#     if message.content.startswith("!atw ") and (message.author.id!=thisbotid) and not message.author.bot:
#         if message.content.startswith("!atw start "):
#             global emj
#             emj=message.content[11:]
#             save_vars()
#             print(emj)
#             if isinstance(get_cached_df('AtWaker_rate_'+str(serverid)),pd.DataFrame) and  isinstance(get_cached_df('AtWaker_data_'+str(serverid)),pd.DataFrame):
#                 renew_db(serverid)
#             else:
#                 make_db(serverid)
#             await channel.send('起動しました。')
#         elif (message.content.startswith("!atw reset ")) and (message.author.id==602203895464329216):
#             if message.content[11:]=='all':
#                 conn.delete('AtWaker_rate_'+str(serverid))
#                 print("rate cache reset")
#                 conn.delete('AtWaker_data_'+str(serverid))
#                 print("data cache reset")
#                 make_db(serverid)
#                 await channel.send('データを全て消去しました。')
#             else:
#                 try:
#                     dbr=get_cached_df('AtWaker_rate_'+str(serverid))
#                     dbd=get_cached_df('AtWaker_data_'+str(serverid))
#                     dbr.drop(message.content[11:],axis=0)
#                     dbd.drop(message.content[11:],axis=0)
#                     cache_df('AtWaker_rate_'+str(serverid),dbr)
#                     cache_df('AtWaker_data_'+str(serverid),dbd)
#                     await channel.send(message.content[11:]+'のデータを消去しました。')
#                 except:
#                     await channel.send('引数が不正です。')
#         elif message.content.startswith("!atw rating "):
#             if isinstance(get_cached_df('AtWaker_rate_'+str(serverid)),pd.DataFrame) and  isinstance(get_cached_df('AtWaker_data_'+str(serverid)),pd.DataFrame):
#                 dbr=get_cached_df('AtWaker_rate_'+str(serverid))
#                 dbd=get_cached_df('AtWaker_data_'+str(serverid))
#                 num=0
#                 print(len(guild.members))
#                 for xx in guild.members:
#                     if message.content[12:] in xx.display_name:
#                         zant=""
#                         num+=1
#                         try:
#                             # if (dbd.iloc[-1].loc[str(xx.id)]==dbd.iloc[-1].loc[str(xx.id)]) and len(dbr)>1:
#                             if len(dbr)>1:
#                                 change=("(+"+str(int(dbr.iloc[-1].loc[str(xx.id)]-dbr.iloc[-2].loc[str(xx.id)]))+")").replace("+-","-")
#                             else:
#                                 change="(--)"
#                         except Exception as e:
#                             print(xx.display_name,e)
#                             change=""
#                         if len(dbd[str(xx.id)].dropna())>0:
#                             try:
#                                 rate=int(dbr.iloc[-1].loc[str(xx.id)])
#                             except Exception as e:
#                                 print(xx.display_name,e)
#                                 rate=dbr.iloc[-1].loc[str(xx.id)]
#                             if(len(dbd[str(xx.id)].dropna())<14):
#                                 zant="(暫定)"
#                         else:
#                             rate=0
#                             zant="(未参加)"
#                         try:
#                             if rate>=2800:
#                                 color='\U0001f534'
#                             elif rate>=2400:
#                                 color='\U0001f7e0'
#                             elif rate>=2000:
#                                 color='\U0001f7e1'
#                             elif rate>=1600:
#                                 color='\U0001f7e3'
#                             elif rate>=1200:
#                                 color='\U0001f535'
#                             elif rate>=800:
#                                 color='\U0001f7e2'
#                             elif rate>=400:
#                                 color='\U0001f7e4'
#                             elif rate>=0:
#                                 color='\U000026aa'
#                             else:
#                                 color=""
#                         except Exception as e:
#                             print(e)
#                             color=""
#                         await channel.send(xx.display_name+':'+str(rate)+color+change+zant)
#                 if num==0:
#                     await channel.send('ユーザーが見つかりません。')
#             else:
#                 await channel.send('初めに!atw start (絵文字)を実行してください。')
#         elif  message.content.startswith("!atw rating-ranking "):
#             if isinstance(get_cached_df('AtWaker_rate_'+str(serverid)),pd.DataFrame):
#                 dbr=get_cached_df('AtWaker_rate_'+str(serverid))
#                 dbd=get_cached_df('AtWaker_data_'+str(serverid))
#                 if len(dbr)>0:
#                     try:
#                         z=max(int(message.content[20:]),1)
#                         for rk in range(z-1,min(z-1+min_display,len(dbr.iloc[-1]))):
#                             try:
#                                 rate=int(dbr.iloc[-1].sort_values(ascending=False).iloc[rk])
#                             except Exception as e:
#                                 print(rk,e)
#                                 rate=dbr.iloc[-1].sort_values(ascending=False).iloc[rk]
#                             userid=int(dbr.iloc[-1].sort_values(ascending=False).index[rk])
#                             zant=""
#                             if guild.get_member(userid)==None:
#                                 username='[deleted]'
#                             else:
#                                 username=guild.get_member(userid).display_name
#                             if len(dbd[str(userid)].dropna())==0:
#                                 zant="(未参加)"
#                             elif len(dbd[str(userid)].dropna())<14:
#                                 zant="(暫定)"
#                             try:
#                                 # if (dbd.iloc[-1].loc[str(userid)]==dbd.iloc[-1].loc[str(userid)]) and len(dbr)>1:
#                                 if len(dbr)>1:
#                                     change=("(+"+str(int(dbr.iloc[-1].loc[str(userid)]-dbr.iloc[-2].loc[str(userid)]))+")").replace("+-","-")
#                                 else:
#                                     change="(--)"
#                             except Exception as e:
#                                 print(e)
#                                 change=""
#                             try:
#                                 if rate>=2800:
#                                     color='\U0001f534'
#                                 elif rate>=2400:
#                                     color='\U0001f7e0'
#                                 elif rate>=2000:
#                                     color='\U0001f7e1'
#                                 elif rate>=1600:
#                                     color='\U0001f7e3'
#                                 elif rate>=1200:
#                                     color='\U0001f535'
#                                 elif rate>=800:
#                                     color='\U0001f7e2'
#                                 elif rate>=400:
#                                     color='\U0001f7e4'
#                                 elif rate>=0:
#                                     color='\U000026aa'
#                                 else:
#                                     color=""
#                             except Exception as e:
#                                 print(e)
#                                 color=""
#                             await channel.send(str(rk+1)+'位:'+username+' '+str(rate)+color+change+zant)
#                     except Exception as e:
#                         print(e)
#                         await channel.send('引数が不正です。')
#                 else:
#                     await channel.send('まだコンテストが開催されていません。')
#             else:
#                 await channel.send('初めに!atw start (絵文字)を実行してください。')
#         elif  message.content.startswith("!atw perf-ranking "):
#             if isinstance(get_cached_df('AtWaker_data_'+str(serverid)),pd.DataFrame):
#                 dbd=get_cached_df('AtWaker_data_'+str(serverid))
#                 try:
#                     a,b=message.content[18:].split()
#                     z=max(int(b),1)
#                     for rk in range(z-1,min(z-1+min_display,len(dbd.loc[a].dropna()))):
#                         perf=int(dbd.loc[a].dropna().sort_values(ascending=False).iloc[rk])
#                         userid=int(dbd.loc[a].dropna().sort_values(ascending=False).index[rk])
#                         if guild.get_member(userid)==None:
#                             username='[deleted]'
#                         else:
#                             username=guild.get_member(userid).display_name
#                         try:
#                             if perf>=2800:
#                                 color='\U0001f534'
#                             elif perf>=2400:
#                                 color='\U0001f7e0'
#                             elif perf>=2000:
#                                 color='\U0001f7e1'
#                             elif perf>=1600:
#                                 color='\U0001f7e3'
#                             elif perf>=1200:
#                                 color='\U0001f535'
#                             elif perf>=800:
#                                 color='\U0001f7e2'
#                             elif perf>=400:
#                                 color='\U0001f7e4'
#                             elif perf>=0:
#                                 color='\U000026aa'
#                             else:
#                                 color=""
#                         except Exception as e:
#                             print(e)
#                             color=""
#                         await channel.send(str(rk+1)+'位:'+username+' '+str(perf)+color)
#                 except Exception as e:
#                     print(e)
#                     await channel.send('引数が不正です。')
#             else:
#                 await channel.send('初めに!atw start (絵文字)を実行してください。')
#         elif message.content=="!atw help":
#             f = open('help.txt', 'r')
#             helpstr = f.read()
#             f.close()
#             await channel.send(helpstr)
#         elif (message.content.startswith("!atw contest_end ")) and (message.author.id==602203895464329216):
#             global num_ra
#             num_ra=1
#             dt=message.content[17:]
#             await contest_end(dt)
#         else:
#             await channel.send('そのコマンドは存在しません。')
#     return
