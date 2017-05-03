# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 09:16:52 2017

@author: trexleraj
"""
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

with open('runtime_ironmaster_2016.txt','r') as f:
    results=f.readlines()

times=[]
for idx,l in enumerate(results):
    m=re.search('(\d{1}):\n',l)
    if m:
        times.append((int(m.group(1))*60)+int(results[idx+1].split(':')[0]))

df=pd.DataFrame(data=times)
df.plot(kind='line')


with open('runtime_chi_marathon.txt','r') as f:
    mara=f.readlines()

mara_total=[]
for x in mara:
    if x[0].isdigit():
        mara_total.append(int(x[0])*60+int(x[2:4]))
    else:
        print 'woo'

with open('runtime_lhu.csv','r') as f:
    lhu=f.readlines()

times=[]
for idx,l in enumerate(lhu):
    m=re.search('(\d{2}):',l)
    if m:
        times.append((int(m.group(1))*60) + int(l[m.start(1)+3:m.start(1)+5]))
        print l,(int(m.group(1))*50) + int(l[m.start(1)+3:m.start(1)+5])
        print ' '
    else:
        print 'no'

df=pd.DataFrame(columns=['total time'],data=sorted(times))
df['pace']=df['total time']/70
ax=plt.figure()
ax=df['pace'].plot(kind='hist')
ax.set_xlabel('pace, min/mile')
ax.set_title('LHU pace')
plt.savefig('lhupace.png')

dfmar=pd.DataFrame(data=sorted(mara_total))
dfboot=pd.DataFrame()
for y in xrange(8):
    subsample=dfmar.sample(n=67).reset_index(drop=True)
    dfboot=pd.concat([dfboot,subsample],1)

dfmar.plot(kind='line')
dfboot['avg']=dfboot.mean(1)
dfboot.sort(columns='avg',inplace=True)
plt.plot(dfboot['avg'].values)

