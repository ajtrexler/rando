# -*- coding: utf-8 -*-
"""
Created on Sun Dec  3 13:40:38 2017

@author: adam
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

DATA_PATH = u'/home/adam/Desktop/edgar'

data = pd.read_csv('171203df_edgar_saved.csv',index_col=0)

logData = pd.read_csv(DATA_PATH+'/edgar_logv10.csv',names=['disposed','numzero','forms'])


rawData = pd.read_csv(DATA_PATH+'/edgar_datav12.csv',names=['amt','price','transdate','querydate','ticker'])
rawData['rownum']=rawData.index

rawData = rawData.drop_duplicates(subset='rownum').drop('rownum',1)

rawData['dow'] = rawData['querydate'].apply(lambda x: datetime.datetime.fromtimestamp(x).isoweekday())
rawData['value']=rawData['amt']*rawData['price']



c,e=np.histogram(rawData['dow'].values,bins=5)

figure1 = plt.figure(figsize=[7,7])
ax=figure1.add_axes([0,0,1,1])
ax.bar(np.arange(1,6,1),c,align='center')
ax.set_xticks(np.arange(1,6,1))
ax.set_xticklabels(['Monday','Tuesday','Wednesday','Thursday','Friday'],rotation=90,size=12)
plt.title('Detected Form4 filings per day',size=15)
plt.ylabel('number of forms',size=15)
figure1.savefig('/home/adam/scripts/sec_fig1.png')

rawData['value'].median()

plt.figure(figsize=[7.5,7.5])
plt.xlabel('Stock price relative to NASDAQ index',size=15)
plt.title('Stock price changes over 3 timescales after EDGAR filing detection',size=15)
plt.ylabel('count',size=15)
for x in xrange(3):
    dval = 'd'+str(x+1)
    mval = 'm'+str(x+1)
    temp = data[dval]/data[mval]
    ub = np.percentile(temp.values,99)
    temp=temp.loc[temp<=ub]
    temp.plot(kind='hist',bins=30,label='epoch'+str(x+1),alpha=0.75)
    print dval,temp.mean(),temp.median()
plt.legend(loc=3)
plt.savefig('/home/adam/scripts/sec_fig2.png')


vb = np.percentile(rawData['value'].values,75)
sTrans = rawData.loc[rawData['value']<=vb]





ub = np.percentile(data['transVol'].values,95)
temp = data.loc[data['transVol']<=ub]['transVol']
edges = np.arange(temp.min(),temp.max(),temp.max()/20)


for v,dc in zip(['transVol','avgVol'],['blue','orange']):
    
    ub = np.percentile(data[v].values,95)
    temp = data.loc[data[v]<=ub][v]
    print v,len(temp)
    c,throw = np.histogram(temp,edges)
    plt.bar(np.arange(0,len(c),1),c,alpha=0.5,label=v,color=dc)
plt.legend()




temp2=data['transVol']/data['avgVol']
temp2 = temp2.loc[temp2<10]
edges2 = np.arange(0,10,10/20.0)
centers = np.arange(0.25,10.25,10/20.0)
vals,throw2 = np.histogram(temp2.values,edges2)

plt.figure(figsize=[7.5,7.5])
plt.bar(np.arange(0,len(vals),1),vals,width=1)
plt.xticks(np.arange(0.5,len(edges2)+0.5,1),np.round(centers,2),rotation=90,horizontalalignment='center')
plt.xlabel('transaction volume / 30-day avg vol, bin centers',size=15)
plt.ylabel('count',size=15)
plt.savefig('/home/adam/scripts/sec_fig3.png')