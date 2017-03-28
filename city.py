# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 21:21:27 2017

@author: adam
"""

import pandas as pd
import numpy as np
import time
import os
import re

cdata=pd.read_csv('/home/adam/Downloads/500city.csv')
cityshort=cdata.loc[1:100]

cities=list(np.unique(cdata['CityName'].values))[1:]
city_states=cdata['CityName']
for x in cities
#keep only cdata from relevant
measures=list(np.unique(cdata['Measure']))
rel_measures=[measures[2],measures[19],measures[23]]
rel_cdata=cdata.loc[cdata['Measure'].apply(lambda x: x in rel_measures)]

datadir=r'/home/adam/scripts/datasets/2015acs/'
filelist=[]
filelist=sorted(os.listdir(datadir))

#fetch the col names from CSV
def get_names(datadir):
    f=filelist[0]
    name=os.path.join(datadir,f)
    reader=open(name,'r')
    topchunk=pd.read_csv(reader,header=None,chunksize=500,dtype='object')
    df=topchunk.get_chunk(size=500)
    return list(df.loc[0,:])
    
#collect data from ACS files
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

#fetch only a subset of the data based on column names.
def get_subset_data(datadir,total,chunk,all_cols,cols_tg):
    data=pd.DataFrame()
    
    for f in filelist:
        name=os.path.join(datadir,f)
        toread=open(name,'r')
        chunks=pd.read_csv(toread,header=None,names=all_cols,dtype='object',chunksize=chunk,usecols=cols_tg)
        df=chunks.get_chunk(size=total)
        data=pd.concat([data,df],ignore_index=True)
    
    del df    
    return data
    
    
start=time.clock()
n=get_names(datadir)

#keep only the relevant columns from the ACS data and del the rest.
relcols=['PUMA','ST','PINCP','SOCP','COW','SCHL','WKW','AGEP','RAC1P','FOD1P','ADJINC','ENG','MAR','MIL','SEX','ANC1P']

##stupid way to check if names i nrelcols are
#for x in relcols:
#    try:
#        alldata[x]
#    except:
#        print 'check',x
        
data=get_subset_data(datadir,1000000,1000000,n,relcols)
[alldata,thorw]=get_data(datadir,500,500)
#[data,filename]=get_data(datadir,10000,10000)
#drop row 0 because it has the column names imported into it.  note that this reindexes the whole business.
#drop rep_weights from end and save as separate dataframe.
data=data.drop([0])
rep_weights=data.iloc[:,203:283]
data=data.drop(rep_weights,axis=1)

data=data.convert_objects(convert_numeric=True)
#need to fillna smartly because sometimes NA means something and sometimes just missing val.
data=data.fillna(-1)

stop=time.clock()
print 'time to load:', (stop-start)/60
def f(st,p):
    return str(int(st)) + '_' + str(int(p))

stp=[f(st,p) for st,p in zip(data['ST'].values,data['PUMA'].values)]   
rpums=pd.Series(data=stp,index=data.index)
data.loc[:,'rPUMA']=rpums
short=data.iloc[1:100]
 
#crossref cities with their PUMA num.  re-index name_table using the combined ST_PUMA notation
name_table=pd.read_table('/home/adam/scripts/datasets/2010_PUMA_Names.txt',delimiter=',')
def f2(st,p):
    return str(int(st)) + '_' + str(int(p))   
name_table.index=[f2(st,p) for st,p in zip(name_table['STATEFP'].values,name_table['PUMA5CE'].values)]


#first narrow by state, then do the idx search in PUMA NAME
fails=[]
city_ids={}
for c in cities:
    loc_state=cdata.loc[cdata['CityName']==c]['StateAbbr'].values[0]
    idx=[i for i,x in enumerate(name_table['PUMA NAME'].values) if re.search(c.lower(),x.lower())]
    if idx:
        city_ids[c]=idx
    else:
        print 'woo!!! nothingness!'
        fails.append(c)
            

#build flatfiles for each condition
for x,n in zip(rel_measures,['binge','prevent','nosleep']):
    local_city=rel_cdata.loc[rel_cdata['Measure']==x]
    local_target
    
    


















measures=[]
for m in np.unique(cdata['Measure']):
    measures.append(m)
    

m=measures[0]
teeth=cdata.loc[cdata['Measure']==m]
teeth.fillna(1,axis=0,inplace=True)

vals=[]
for city in np.unique(teeth['CityName']):
    if city != 1:
        local=teeth.loc[teeth['CityName']==city]
        vals.append((city,local['StateAbbr'].values[0],local['Data_Value'].mean(),local['Data_Value'].std()))


def sbym(x):
    return x[2] 

sv=sorted(vals,key=sbym,reverse=True)

#older adult men preventative, m[19]
#sleeping less than 7 hours, m[23]
#binge drinking, m[2]

#ident the unique cities in the cdata set.


#extract PUMA data


