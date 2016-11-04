# -*- coding: utf-8 -*-
"""
Created on Wed Nov 02 15:14:40 2016

@author: trexleraj
"""

import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
from datetime import datetime
import seaborn as sea

data=pd.read_csv('logc.csv',header=1)
q=data.dropna(0)

#put the dates in datetime format and return a converted dict with datetime keys.
def convert_date(ac_per_day):
  ac_per_day_c={}  
  for row in ac_per_day:
    val=ac_per_day[row]    
    
    date=datetime.strptime(row,'%m/%d/%Y')
  
    ac_per_day_c[date]=val
  return ac_per_day_c
  

def day_of_week(output):
  days={}  
  for row in output:
    d=row.weekday()
    dval=output[row]
    if d not in days:
      days[d]=dval
    else:
      days[d]+=dval
  return days  
  
log=data['Image Type']
dates=data['Date']
ac_per_day={}
acqtype={}
beads=0
acq=0

for line,d in zip(log,dates):
    if str(line)!='nan':
        #look first in line and parse beads and image types.  build acqtype dict.
        beadpat=re.search('bead',line)
        if beadpat:
            beads+=1
    
        else:
            acq+=1
            typepat=re.search('(\w+)',line)
            if typepat:
                entry=typepat.group(0).lower()
                if  entry not in acqtype:
                    acqtype[entry]=1
                else:  
                    acqtype[entry]+=1
    if str(d)!='nan':
        numcheck=re.search('\d+',d)
        if numcheck:
            if d not in ac_per_day:
                ac_per_day[d]=1
            else:
                ac_per_day[d]+=1

#convert to datetime dict
output=convert_date(ac_per_day)

#make a time series from the dict, resample daily and then fill the NaN values 
#that resample puts in with 0.
ts=pd.Series(output)
ts_resampled=ts.resample('D',fill_method=None).mean()
ts_resampled.fillna(0,inplace=True)
fig1=plt.plot(ts_resampled)
plt.xticks(rotation=90)
plt.ylabel('acquisitions per day')
plt.savefig('acq_per_day.png')

#only major acqtypes
def maj(y):
    return acqtype[y]
fig2=plt.figure(figsize=[5,5])
fig2=plt.pie(sorted(acqtype.values(),reverse=True)[0:4],labels=sorted(acqtype,key=maj,reverse=True)[0:4])
plt.suptitle('major imaging types used',size=15)
plt.savefig('piegraph.png')


#make day of the week images acquired bar plot
td=day_of_week(output)
td_series=pd.Series(td.values())
day_key=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
td_series.index=day_key
td_series.plot(kind='bar')
plt.savefig('daysofweek.png')



#make plot of weekly output over time, make var to show mean weekly ouput
#need to reset idx for 1,2,3 etc.
tw=pd.Series(index=output.keys(),data=output.values())
tw_resampled=tw.resample('W').sum()
tw_resampled.fillna(0,inplace=True)
tw_resampled.plot()

zeroweeks=(tw_resampled==0).sum()
grindscore=round(float((float(len(tw_resampled)-zeroweeks))/len(tw_resampled)),2)

#make combined graph of daily and weekly outputs now shown on same plot.
fig3=plt.figure()
plt.xticks(rotation=90)
plt.plot(ts)
plt.plot(tw_resampled)
plt.savefig('combined.png')

print 'average acquisitions per total days:',ts_resampled.mean()
print 'average acquisitions per day I imaged:',ts.mean()
print 'percentage of weeks I imaged since starting:',grindscore

              




