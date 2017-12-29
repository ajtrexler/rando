# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 09:16:52 2017

@author: trexleraj
"""
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

wser=pd.read_csv('runtime_wser.csv',header=None)
wser.columns=['place','time','bib','name','lastname','gender','age','city','state']

def convert_time(x):
    return ( (int(x[0:2])*60)+(int(x[3:5])) ) / 60.0

wser['hours']=wser['time'].apply(convert_time)


wser_time=[]
for x in wser['time']:
    wser_time.append(((int(x[0:2])*60)+(int(x[3:5])))/60.0)

plt.plot(sorted(wser_time))


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
#        print l,(int(m.group(1))*50) + int(l[m.start(1)+3:m.start(1)+5])
#        print ' 'print x
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

class race_results():
    def __init__(self,name,fname,data_flag):
        self.name=name
        self.fname=fname
        
        def parse_time1(t):
            numhour=len(t.split(':')[0])
            m=re.search(r'(\d{%x}):'%numhour,str(t))
            if m:
                return ((int(m.group(1))*60) + int(t[m.start(1)+3:m.start(1)+5])) / 60.0 

  
        if data_flag== 'csv':
            data=pd.read_csv(fname,header=None)
            #identify which column contains timing data.  must have 1 digit followed by ':'
            timecol='flag'
            for x in data:
                m=re.search('(\d{1}):',str(data[x][2]))
                if m:
                    timecol=x
                    self.times=data[timecol].apply(parse_time1)
                    break
            if timecol=='flag':
                self.times='error'
                print 'couldnt find the data column with time data'


            
            
        elif data_flag=='txt':
            with open(fname,'r') as f:
                data=f.readlines()
            times=[]
            for x in data:
                if x[0].isdigit():
                    times.append((((int(x.split(':')[0])*60)+(int(x.split(':')[1]))) / 60.0))
            self.times=times  
    
    def plot_time(self,k):
        #k=kind of plot
        df=pd.DataFrame(data=sorted(self.times))
        ax=plt.figure()
        ax=df.plot(kind=k,legend=None)
        ax.set_xlabel('total time (hours)')
        ax.set_title('{} total time'.format(self.name))
        

