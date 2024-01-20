# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 17:46:15 2017

@author: user
"""


import strategy.popular_model as popmoder 
import talib
import datetime 
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import urllib.request; #用來建立請求


def arron(parmam) :
    star = parmam[0]
    price= parmam[1]
    ex_handle= parmam[2]
    buy_list= parmam[3]
    sell_list= parmam[4]
    data_list = parmam[5]
    data_list2= parmam[6]
    data_list3= parmam[7]
    start= parmam[8]
    end = parmam[9]
    str_tmp= parmam[10]
    ope= parmam[11]
    close= parmam[12]
    high= parmam[13]
    low= parmam[14]
    vol= parmam[15]
    date= parmam[16]
    date_ex= parmam[17]
    now_stock= parmam[18]
    model= parmam[19]

    #技術指標
    #arron=talib.AROONOSC(np.array(high), np.array(low), timeperiod=60)
    aroonup,aroondown= talib.AROON(np.array(low),np.array(high),timeperiod=60)
    #=talib.AROON(np.array(high), timeperiod=60)
    SMA = talib.MA(np.array(close), timeperiod=10, matype=0) 
    #print(aroonup,aroondown)
    
    
    #交易策略
    deposit=[]
    win=[]
    win_con=[0]
    los_con=[0]
    buy_data=[]
    self_data=[]
    buy_date=[]
    self_date=[]
   
    # star=10000000 #一開始的錢
    # price=10000000
    fin_price=0
    handle=0       #持有股數
    re_handle=0    #實際持有
    assets = 0
    # model= "gen"
    buy_list_dict =[]
    sell_list_dict =[]
    for tmp in range(60,len(aroonup)):
        if(tmp+1<len(aroonup)):
            ex_handle=(int(price/(close[tmp]*1000))-1)
            if(model == "gen"):
                if(aroonup[tmp]>aroondown[tmp] and tmp>start and tmp<end  ):
                    data_count_num =  tmp +1
                    total_date_count =data_count_num
                    total_date_str= date[data_count_num]
                    ex_data_list = data_list[data_count_num]
                    ex_data_list = ex_data_list+ ((total_date_count), total_date_str)
                    buy_list.append(ex_data_list)
                    buy_list_dict.append(data_count_num)
                    
                    # print(ex_data_list)
             
                elif (aroonup[tmp]<aroondown[tmp] and tmp>start and tmp<end ):
                    data_count_num =  tmp 
                    total_date_count = data_count_num 
                    total_date_str = date[data_count_num]
                    ex_data_list = data_list[data_count_num]
                    ex_data_list = ex_data_list + ((total_date_count), total_date_str)
                    sell_list.append(ex_data_list)
                    sell_list_dict.append(data_count_num)
                    # print(ex_data_list)
            else:
                if(aroonup[tmp]>aroondown[tmp] and tmp>start and tmp<end   and ex_handle >=1 and price >= (ex_handle*close[tmp]*1000)):
                    handle= handle+ex_handle*1000
                    re_handle=re_handle+ex_handle
                    fin_price=price-(ex_handle*ope[tmp+1])*1000  #1=1000
                    print ('買進日期',date[tmp+1],'開盤價',ope[tmp+1],'支出',(ex_handle*ope[tmp+1])*1000,'結算金額',fin_price,'持有股數',handle,'持有張數',re_handle)
                    str_record='買進日期',date[tmp+1],'開盤價',ope[tmp+1],'支出',(ex_handle*ope[tmp+1])*1000,'結算金額',fin_price,'持有股數',handle,'持有張數',re_handle
                    buy_data.append(str_record)
                    buy_list.append(data_list[tmp+1])
                    # print(data_list[tmp+1])
                    price= fin_price
                elif (aroonup[tmp]<aroondown[tmp] and re_handle >=1 and tmp>start and tmp<end ):
                    fin_price=price+(re_handle*close[tmp])*1000
                    handle=0 
                    re_handle=0
                    print ('賣出日期',date[tmp],'收盤價',close[tmp],'結算金額',fin_price,'持有股數',handle,'持有張數',re_handle)
                    str_record='賣出日期',date[tmp],'收盤價',close[tmp],'結算金額',fin_price,'持有股數',handle,'持有張數',re_handle
                    self_data.append(str_record)
                    sell_list.append(data_list[tmp])
                    # print(data_list[tmp+1])
                    price= fin_price
            if(fin_price-star > 0 ):
                assets = int( fin_price-star)
                deposit.append([ date[tmp] , assets])      
    if(model == "gen"):
        return [buy_list,sell_list,set(buy_list_dict),set(sell_list_dict)]

    df = pd.DataFrame(deposit, columns=list(['date','deposit'])) 
    df.to_csv("./price2.csv", index=False)
    
    if (handle>0):#強制平倉
        fin_price+= (close[len(close)-1]*handle)
        handle=0
        re_handle=0   
        print ('強制平倉 賣出日期',date[len(close)-1],'收盤價',close[len(close)-1],'結算金額',fin_price,'持有股數',handle,'持有張數',re_handle)

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
    print ('交易紀錄')
    print ('-----------------------------------')
    print("now_stock",now_stock)
    print ('-----------------------------------')
    print ('初始金額:',(int(star)))
    print ('獲利金額:',(int(assets)))
    print ('結算金額:',(int(fin_price)))
    print ('交易次數 買/賣:',len(buy_data),'/',len(self_data))
    print ('總交易次數:',sum((len(buy_data),len(self_data))))    
    if(len(buy_data) != 0):
        print ('勝率:%5.2f'%(count/sum((len(buy_data),len(self_data)))*100),"%")
        print ('報酬率:',round(((fin_price-star)/star)*100,2))
        print ('報酬率:%5.2f'%(((fin_price-star)/star)*100),"%")
        print ('平均報酬率',round((((fin_price-star)/star))/(sum((len(buy_data),len(self_data))))*100,4),"%")
        print("獲勝次數:",count)
        print("虧損次數:",loss)     
        print("最大獲利率:",round(max(win_con),2),"%")
        print("最大虧損率:",round(min(los_con),2),"%")
        str_tmp='初始金額:'+str((int(star)))+"\n"+'獲利金額:'+str((int(fin_price-star)))+"\n"+'總收入金額:'+str((int(fin_price)))+"\n"+'交易次數 買/賣:'+str(len(buy_data))+'/'+str(len(self_data))+"\n"+'總交易次數:'+str(sum((len(buy_data),len(self_data))))+"\n"+'勝率:'+str((count/sum((len(buy_data),len(self_data)))*100))+'%'+"\n"+'報酬率:'+str(((fin_price-star)/star)*100)+'%'+"\n"+'平均報酬率:'+str(round((((fin_price-star)/star))/(sum((len(buy_data),len(self_data))))*100,4))+'%'+"\n"+'獲勝次數'+str(count)+"\n"+'虧損次數:'+str(loss)+"\n"+'最大獲利率:'+str(round(max(win_con),2))+'%'+"\n"+'最大虧損率:'+str(round(min(los_con),2))+'%'
    else:
        print("沒有發生交易")
        str_tmp = "沒有發生交易"
    return str_tmp
