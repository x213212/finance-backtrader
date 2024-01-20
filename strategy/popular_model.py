
import datetime 
import numpy as np
import talib
import warnings
import requests
import pandas as pd
import threading
import time
import tkinter as tk
from io import StringIO
import os
warnings.filterwarnings('ignore')
import urllib.request; #用來建立請求
import statistics
global download 
from itertools import tee
import scipy.stats as stats

#技術指標
def get_MACD(close):
    MACD = talib.MACD(close,fastperiod=12, slowperiod=26, signalperiod=9)  
    return [float(x) for x in MACD [1]]
    
def get_DIF(close):
    DIF=[]
    EMA12=talib.EMA(close, timeperiod=12)  
    EMA26=talib.EMA(close, timeperiod=26)
    for tmp in range(0,len(EMA12)):
        DIF.append(float(EMA12[tmp]-EMA26[tmp]))
    return DIF

def get_BBand(close):
    #BBband
    BBand = talib.BBANDS(close,timeperiod=20,nbdevup=1.5,nbdevdn=1.5)
    return BBand 

def get_OSC(macd,dif):
    OSC=[]
    for tmp in range(0,len(macd),1):
        OSC.append(float(macd[tmp]-dif[tmp]))
    return OSC

def get_SMA(close):
    SMA= talib.MA(np.array(close), timeperiod=10, matype=0)
    return SMA

def get_RSI(close):
    RSI = talib.RSI(close, timeperiod=14)
    return RSI

def get_ATR(high,low,close):
    podongPrice=talib.ATR(high,low,close,timeperiod=14)
    return podongPrice

def get_NATR(high,low,close):
    natrPrice=talib.NATR(high,low,close,timeperiod=14)
    return natrPrice

def get_fastktd(high,low,close):
    fastk, fastd = talib.STOCHF(high, low,close, fastk_period=60, fastd_period=7, fastd_matype=0)
    return (fastk,fastd)

def get_KDJ(high,low,close):
    indicators={}

    high_prices = high
    low_prices = low
    close_prices =close
    indicators['k'], indicators['d'] = talib.STOCH(high_prices, low_prices, close_prices, 
                                                   fastk_period=6, 
                                                   slowk_period=4, 
                                                   slowd_period=4)
    indicators['j'] = 3 * indicators['k'] - 2 * indicators['d']
    return indicators

def is_trend_steady(data):
    if statistics.stdev(data) < statistics.mean(data) * 0.1:
        return "Steady"
    elif statistics.stdev(data) > statistics.mean(data) * 0.1:
        return "Volatile"
    else:
        return "Unknown"

def is_trend_increasing(data):
    a, b = tee(data)
    next(b, None)
    return all(x <= y for x, y in zip(a, b))

def is_trend_decreasing(data):
    a, b = tee(data)
    next(b, None)
    return all(x >= y for x, y in zip(a, b))

def cox_stuart(list_c,debug=False):
	lst=list_c.copy()
	raw_len=len(lst)
	if raw_len%2==1:
		del lst[int((raw_len-1)/2)]    # 删除中位数
	c=int(len(lst)/2)
	n_pos=n_neg=0
	for i in range(c):
		diff=lst[i+c]-lst[i]
		if diff>0:
			n_pos+=1
		elif diff<0:
			n_neg+=1
		else:
			continue
	num=n_pos+n_neg
	k=min(n_pos,n_neg)           #  双边检验
	print("k: ",k)
	print("num:",num)
	p_value=2*stats.binom.cdf(k,num,0.5)  #  二项分布
	if debug:
		print('fall:%i, rise:%i, p-value:%f'%(n_neg, n_pos, p_value))
	if n_pos>n_neg and p_value<0.05:   #  双边检验
		return 'increasing'
	elif n_neg>n_pos and p_value<0.05:  #  双边检验
		return 'decreasing'
	else:
		return 'no trend'

def get_today_tw(today):
    global download 
    global df_tmp
    df_tmp=[]
    download = False
    # 建立一個子執行緒
    t = threading.Thread(target = download_job(today))

    # 執行該子執行緒
    t.start()
   
    download = False
    return df_tmp
    


def download_job(today):
    global download 
    global df_tmp
    file_path = "./history_data/"+today+"statements.csv"
    if ( os.path.isfile(file_path)):
        print("File exists!")
        df = pd.read_csv("./history_data/"+today+"statements.csv")
        df_tmp= df
    else:
        print("File not found!")
        headers = {'Host': 'en.savefrom.net', 'Connection': 'keep-alive', 'Content-Length': '119',
       'Cache-Control': 'max-age=0',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
       'Origin': 'http://en.savefrom.net','Upgrade-Insecure-Requests': '1',
       'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
       'Content-Type': 'application/x-www-form-urlencoded',
       'Referer': 'http://en.savefrom.net/',
       'Accept-Encoding': 'gzip, deflate',
       'Accept-Language': 'en-US,en;q=0.8'} # ,
       #'Cookie': 'lang=en; PHPSESSUD=2c217930b58d07b38034ac6ca091405b; PHPSESSID=bjmp1vln6vjcf5q16q90f62v62; rmode=true; _ga=GA1.2.635523328.1446793104'}

        payload = {'sf_url':'example.com'}
        try:
            r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + today + '&type=ALL')
            df = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '}) 
                                             for i in r.text.split('\n') 
                                             if len(i.split('",')) == 17 and i[0] != '='])), header=0)
            df_tmp= df
            df.to_csv("./history_data/"+today+"statements.csv", index=False)
            
            print (today +"download sucessful!")
            r.close()
        except:
            print ("something error download fail!")
            
        
    download = True
    