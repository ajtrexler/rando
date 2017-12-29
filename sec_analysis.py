# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 15:28:55 2017

@author: adam
"""

import requests
import pandas as pd
import datetime 
import matplotlib.pyplot as plt
import quandl
import numpy as np

DATA_PATH = u'/home/adam/Desktop/edgar'
with open('/home/adam/data/keys/quandlkey.txt','r') as f:
    qkey = f.readline().split('\n')[0]
quandl.ApiConfig.api_key = qkey


logData = pd.read_csv(DATA_PATH+'/edgar_logv10.csv',names=['disposed','numzero','forms'])
logData

rawData = pd.read_csv(DATA_PATH+'/edgar_datav12.csv',names=['amt','price','transdate','querydate','ticker'])
rawData['rownum']=rawData.index

rawData = rawData.drop_duplicates(subset='rownum').drop('rownum',1)

rawData['dow'] = rawData['querydate'].apply(lambda x: datetime.datetime.fromtimestamp(x).isoweekday())

nasdaq = quandl.get('NASDAQOMX/NQUSB')
datesInterest = [1,7,30]      


def timejump(data,j):
    price = 0
    while price==0:
        nDay = datetime.datetime.strftime(datetime.datetime.strptime(day0,'%Y-%m-%d')+datetime.timedelta(days=j),'%Y-%m-%d')
        try:
            price=data.loc[nDay]['Close']
            vol=data.loc[nDay]['Volume']
            market=nasdaq.loc[nDay]['Index Value']
        except:
            j=j+1
    return price,vol,market

def getpreavgvol(data,j,sDay):
    vol=0
    volArr=[]
    pDay = sDay
    for x in xrange(j):
        pDay = datetime.datetime.strftime(datetime.datetime.strptime(pDay,'%Y-%m-%d')+datetime.timedelta(days=-1),'%Y-%m-%d')
        while pDay not in data.index:
            pDay = datetime.datetime.strftime(datetime.datetime.strptime(pDay,'%Y-%m-%d')+datetime.timedelta(days=-1),'%Y-%m-%d')
        vol=data.loc[pDay]['Volume']
        volArr.append(vol)
    return volArr        

def parseTicker(ticker,data):
    dates = rawData.loc[rawData['ticker']==ticker]['querydate']
    dfOut = pd.DataFrame()
    for d in dates:
        day0 = datetime.datetime.strftime(datetime.datetime.fromtimestamp(d),'%Y-%m-%d')
    
        prices = [data.loc[day0]['Close']]
        volumes = [data.loc[day0]['Volume']]
        marketvals = [nasdaq.loc[day0]['Index Value']]
        for i,n in enumerate(datesInterest):
            p,v,m=timejump(data,n)
            prices.append(p)
            volumes.append(v)
            marketvals.append(m)
        volArr=getpreavgvol(data,30,day0)
        writeVals={}
        writeVals['init']=prices[0]
        pArr = [p/float(prices[0]) for p in prices][1:]
        for i,p in enumerate(pArr):
            writeVals['d'+str(i+1)]=p
        writeVals['avgVol']=np.mean(volArr)
        writeVals['stdVol']=np.std(volArr)
        writeVals['transVol']=volumes[0]
        mArr = [p/float(marketvals[0]) for p in marketvals][1:]
        for i,p in enumerate(mArr):
            writeVals['m'+str(i+1)]=p
        df = pd.DataFrame.from_dict(orient='index',data=writeVals).transpose()
        #stamp = str(d).split('.')[0]
        df.index=[str(d)+ticker]
        dfOut = pd.concat([df,dfOut],0)
    return dfOut
        

e=0
t=0
bulkDF = pd.DataFrame()
for ticker in rawData['ticker'].unique():
    code = 'WIKI/'+ticker
    try:
        data = quandl.get(code)
        toadd = parseTicker(ticker,data)
        bulkDF = pd.concat([bulkDF,toadd],0)
        t=t+1
        if t % 10==0: print t
    except:
        e=e+1
        if e % 10==0: print e
