# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 14:58:52 2016

@author: adam
"""

import pandas as pd
import numpy as np
import time
import os
import seaborn as sea 
import matplotlib.pyplot as plt
from pandas.tools.plotting import table

#zillow data
#prices=pd.read_csv('/home/adam/scripts/datasets/City_MedianValuePerSqft_AllHomes.csv')

#ACS kaggle data
#filename=r'ss13pusa.csv'
#filename2=r'ss13pusb.csv'
datadir='/home/adam/scripts/datasets/acs/'

filelist=[]
filelist=sorted(os.listdir(datadir))
bulk_data=pd.DataFrame()

#get the data.  load a defined amount from both csv files in a defined chunksize.
def get_data(datadir,total,chunk):
    data=pd.DataFrame()
    
    for f in filelist:
        name=os.path.join(datadir,f)
        toread=open(name,'r')
        chunks=pd.read_csv(toread,header=None,dtype='object',chunksize=chunk)
        df=chunks.get_chunk(size=total)
        data=pd.concat([data,df],ignore_index=True)
    
    data.columns=list(data.loc[0,:])
    del df    
    return data,name

start=time.clock()

[bulk_data,filename]=get_data(datadir,10000000,10000)

stop=time.clock()
print 'time to load:', (stop-start)/60

##make name_table, which combines the descriptive names of PUMAs with PUMA id used here.
name_table=pd.read_table(os.path.join('/home/adam/scripts/datasets','2010_PUMA_Names.txt'),delimiter=',')
def f2(st,p):
    return str(int(st)) + '_' + str(int(p))
    
name_table.index=[f2(st,p) for st,p in zip(name_table['STATEFP'].values,name_table['PUMA5CE'].values)]

#data to get:
#   RNTP- monthly rent, use ADJHSG to adjust to constant dollar
#   FINCP- family income, use ADJINC to adjust to constant dollar
#   MRGP- first mortgage payment, use ADJHSG to adjust to constant dollar
#   SMP- all second and junior mortgages, use ADJHSG to adjust to constant dollar
#   PUMA, obvs
#   PAP- public assistance income, use ADJINC to adjust to constant dollar
#   TAXP- yearly property taxes, this is a categorical, see datadict for table.
#   NP-need to normalize to family size as proxy for square footage
feat_list=['RNTP','FINCP','MRGP','SMP','PUMA','ST','TAXP','ADJINC','ADJHSG','NP']
data=pd.DataFrame(columns=feat_list,data=bulk_data[feat_list])
data.fillna(0,inplace=True)
for x in data:
    data[x]=pd.to_numeric(data[x],errors='coerce')
rownan=data.isnull().any(axis=1)
data.drop(rownan.loc[rownan==True].index,0,inplace=True)

data['atotMRG']=(data['MRGP']+data['SMP'])*(data['ADJHSG']/1000000)
data['aRNTP']=data['RNTP']*(data['ADJHSG']/1000000)
data['aFINCP']=data['FINCP']*(data['ADJINC']/1000000)

#list all the PUMAs
def f(st,p):
    return str(int(st)) + '_' + str(int(p))

stp=[f(st,p) for st,p in zip(data['ST'].values,data['PUMA'].values)]   
rpums=pd.Series(data=stp,index=data.index)
data.loc[:,'rPUMA']=rpums 
data.set_index(keys='rPUMA',inplace=True)

#get a list of all the PUMAs.
pumlist=[]
for pums in data.index.values:
    if pums not in pumlist:
        pumlist.append(pums)
        
#build new df to show average values for everything we care about
def stats(v):
    m=np.mean(v.ix[v.values.nonzero()])
    stm=np.std(v.ix[v.values.nonzero()])
    return m,stm

stats_df=pd.DataFrame(columns=['maMRG','staMRG','maRNTP','staRNTP','maFINCP','staFINCP','count','rentNP','ownNP'])
for q in pumlist:
    loc_df=pd.DataFrame(columns=['maMRG','staMRG','maRNTP','staRNTP','maFINCP','staFINCP','count','rentNP','ownNP'])
    local=data.loc[q]
    loc_df.loc[q,'count']=len(local)
    loc_df['rentNP']=(local.loc[local['RNTP']>0,'NP']).mean()
    loc_df['ownNP']=(local.loc[local['atotMRG']>0,'NP']).mean()
    loc_df.loc[q,['maMRG','staMRG']]=stats(local['atotMRG'])
    loc_df.loc[q,['maRNTP','staRNTP']]=stats(local['aRNTP'])
    loc_df.loc[q,['maFINCP','staFINCP']]=stats(local['aFINCP'])
    stats_df=pd.concat([stats_df,loc_df],0)

stats_df['normMRG']=(stats_df['maMRG']/stats_df['ownNP'])/stats_df['maFINCP']
stats_df['normRNTP']=((stats_df['maRNTP']*12)/stats_df['rentNP'])/stats_df['maFINCP']
stats_df['rent_afford']=stats_df['normMRG']/stats_df['normRNTP']
stats_df.sort_values(by='rent_afford',ascending=False,inplace=True)

plt.figure(figsize=[5,5])
sea.jointplot(x=stats_df['rent_afford'],y=stats_df['maFINCP'])
plt.savefig('rent_fig2.png')

plt.figure(figsize=[5,5])
plt.xlabel('sorted PUMAs')
plt.ylabel('rent_afford parameter')
plt.scatter(x=np.arange(0,len(stats_df),1),y=stats_df['rent_afford'])
plt.savefig('rent_fig1.png')

topten=stats_df.ix[0:9].index.values 
bottomten=stats_df.ix[-9:].index.values

tb=pd.concat([stats_df.ix[0:10],stats_df.ix[-10:]])
tb_names=name_table.loc[tb.index]
print tb_names['PUMA NAME']









