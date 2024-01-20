# -*- coding: utf-8 -*-
"""
Created on Sat Dec 23 17:48:25 2017

@author: user
"""


import csv
import os
import numpy as np
import talib
import pandas as pd

num_48 = ["1301台塑"]
df=pd.DataFrame()
df2=pd.DataFrame(num_48)
for iii in num_48:    
    str=os.path.join("C:\\","Users","x2132","OneDrive","桌面","History_data",iii) 
    str=str+'.csv'
    print(str)
    with open(str,'r') as o:
        reader=csv.DictReader(o)
        o=[row["開盤"] for row in reader] #要導入的列
    with open(str,'r') as c:
        reader=csv.DictReader(c)
        c=[row["收盤"] for row in reader] #要導入的列
    with open(str,'r') as h:
        reader=csv.DictReader(h)
        h=[row["最高"] for row in reader] #要導入的列
    with open(str,'r') as l:
        reader=csv.DictReader(l)
        l=[row["最低"] for row in reader] #要導入的列
    with open(str,'r') as d:
        reader=csv.DictReader(d)
        d=[row["日期"] for row in reader]
        
        ope = [float(x) for x in o]
        close = [float(x) for x in c]
        high = [float(x) for x in h]
        low = [float(x) for x in l]
        date =d
        
        
#島狀反轉出場條件
    SMA = talib.MA(np.array(close), timeperiod=10, matype=0)
#交易策略
    win=[]
    win_con=[0]
    los_con=[0]
    buy_data=[]
    self_data=[]
    buy_date=[]
    self_date=[]
    star=100000 #一開始的錢
    price =100000 #總結
    
    handle=0       #持有股數
    ex_handle=1    #持有股數上限
    re_handle=0    #實際持有
    n=0.03 #跳空趴數
    cb=[]
    ob=[]

    for tmp in range(0,len(ope)):
        if(tmp+1<len(ope)):
            cb.append(close[tmp])
            ob.append(ope[tmp])
            if len(cb)==3 and len(ob)==3 :
                #print('收盤',cb)
                #print('開盤',ob) 
                if ob[0]>ob[0] and cb[0]>cb[1] and cb[2]>ob[2] and ob[2]>cb[0]*(1+n): 
                    handle= handle+ex_handle*1000
                    re_handle=re_handle+ex_handle
                    fin_price=price-(ex_handle*ope[tmp+1])*1000  #1=1000
                    print('買進日期',date[tmp+1],'開盤價',ope[tmp+1],'支出',(ex_handle*ope[tmp+1])*1000,'結算金額',fin_price,'持有股數',handle,'持有張數',re_handle)
                    str='買進日期',date[tmp+1],'開盤價',ope[tmp+1],'支出',(ex_handle*ope[tmp+1])*1000,'結算金額',fin_price,'持有股數',handle,'持有張數',re_handle
                    buy_data.append(str)
                    price= fin_price
                else :
                     if(handle >0):
                       if close[tmp]<SMA[tmp]:
                        fin_price=price+(re_handle*close[tmp])*1000
                        handle=0 
                        re_handle=0
                        print('賣出日期',date[tmp],'收盤價',close[tmp],'結算金額',fin_price,'持有股數',handle,'持有張數',re_handle)
                        str='賣出日期',date[tmp],'收盤價',close[tmp],'結算金額',fin_price,'持有股數',handle,'持有張數',re_handle
                        self_data.append(str)
                        price= fin_price
                del ob[0]
                del cb[0]

    if (handle>0):#強制平倉
       fin_price+= (close[len(close)-1]*handle)
       handle=0
       re_handle=0   
       print ('強制平倉 賣出日期',date[len(close)-1],'收盤價',close[len(close)-1],'結算金額',fin_price,'持有股數',handle,'持有張數',re_handle)
    del ope[tmp]
    del close[tmp]
    

#回測績效 - 交易次數
  
    count=0
    loss=0
    for a,b in zip (buy_data[:],self_data[:]):
         buy_date.append(a[3])
         self_date.append(b[3])
         if buy_date[0]<self_date[0]:
             count+=1
         else:
             loss+=1
         del buy_date[0]
         del self_date[0]

    for a,b in zip (buy_data[:],self_data[:]):
         buy_date.append(a[3])
         self_date.append(b[3])
         if len(buy_date)>0:
             z=(self_date[0]-buy_date[0])/buy_date[0]
             if z>0:
                win_con.append(z)                 
             elif z<0:
                los_con.append(z)
         del buy_date[0]
         del self_date[0]
    for tmp in buy_data:
        print (tmp)
    for tmp in self_data:
        print (tmp)
     
    wp=int(fin_price-star)
    buy=len(buy_data)
    sel=len(self_data)
    total_trade=sum((len(buy_data),len(self_data)))
    win_rate=round(count/sum((len(buy_data),len(self_data)))*100,2)
    retur=round(((fin_price-star)/star)*100,2)
    ave_retur=round((((fin_price-star)/star))/(sum((len(buy_data),len(self_data))))*100,4)
    win_num=count
    los_num=loss
    max_win=round(max(win_con),2)
    min_los=round(min(los_con),2)
    
#    
#    data={"獲利金額":[wp],"買次數":[buy],"賣次數":[sel],"總交易次數":[total_trade],"勝率":[win_rate],"報酬率":[retur],"平均報酬率":[ave_retur],"獲利次數":[win_num],"虧損次數":[los_num],"最大獲利率":[max_win],"最大虧損率":[min_los]}
#    df=df.append(pd.DataFrame(data),ignore_index=True)
#df.insert(0,'股票代號',df2)
#df.to_csv("島狀反轉.KPI.csv")         
print ('獲利金額:',(int(fin_price-star)))
print ('交易次數 買/賣:',len(buy_data),'/',len(self_data))
print ('總交易次數:',sum((len(buy_data),len(self_data))))    
print ('勝率:%5.2f'%(count/sum((len(buy_data),len(self_data)))*100),"%")
print ('報酬率:',round(((fin_price-star)/star)*100,2))
print ('報酬率:%5.2f'%(((fin_price-star)/star)*100),"%")
print ('平均報酬率',round((((fin_price-star)/star))/(sum((len(buy_data),len(self_data))))*100,4),"%")
print("獲勝次數:",count)
print("虧損次數:",loss)     
print("最大獲利率:",round(max(win_con),2),"%")
print("最大虧損率:",round(min(los_con),2),"%")
