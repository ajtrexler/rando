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
import sqlite3

cdata=pd.read_csv('/home/adam/Downloads/500city.csv')
cityshort=cdata.loc[1:100]

cities=list(np.unique(cdata['CityName'].values))[1:]
city_states=cdata['CityName']

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
relcols=['PUMA','ST','PINCP','SOCP','SEMP','MIG','JWTR','JWMNP','CIT','INDP','JWAP','NOP','COW','SCHL','WKW','AGEP','ANC2P','RAC1P','FOD1P','ADJINC','ENG','MAR','MIL','SEX','ANC1P']

#stupid way to check if names i nrelcols are
for x in relcols:
    if x not in n:
        print 'check',x
        
data=get_subset_data(datadir,10000000,10000,n,relcols)
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
state_table=pd.read_csv('/home/adam/scripts/datasets/puma_state_id.csv')
#parse the two letter state code from state_table
def p_state_table(x):
    r=re.search('/(\w{2})',x)
    if r:
        return r.group(1)
    else:
        return 'blah'
state_abbr=state_table['Unnamed: 1'].apply(p_state_table)
state_abbr_dict=dict(zip(state_abbr,state_table['State Code']))

def f2(st,p):
    return str(int(st)) + '_' + str(int(p))   
name_table.index=[f2(st,p) for st,p in zip(name_table['STATEFP'].values,name_table['PUMA5CE'].values)]

#first narrow by state, then do the idx search in PUMA NAME
fails=[]
city_ids={}
for c in cities:
    loc_state=cdata.loc[cdata['CityName']==c]['StateAbbr'].values[0]
    loc_table=name_table.loc[name_table['STATEFP']==state_abbr_dict[loc_state]]
    idx=[i for i,x in enumerate(loc_table['PUMA NAME'].values) if re.search(c.lower(),x.lower()) ]
    if idx:
        city_ids[c]=list(loc_table.ix[idx].index.values)
    else:
        fails.append(c)

'''
build the SQL table that will hold the flat files for each condition
convoluted method to create column names in the SQL tables based on what the 
column names in the dataframes are.  it should work generally for however many columns are used.

'''
conditions=['binge','prevent','nosleep']   
sql_file='cityhealth_demo.sqlite'
l=[]
for x in short.columns.values:
    if x != 'rPUMA':
        l.append(x+' '+'INT,')
    else:
        l.append(x+' '+'STR')

c=''.join(l)
c=c+', entry INT, target DECIMAL'
c=c+',PRIMARY KEY (entry)'

if not os.path.isfile(sql_file):
    db=sqlite3.connect(sql_file)
    db.text_factory='str'     
    conn=db.cursor()
    for x in conditions:
        conn.execute('CREATE TABLE {tn} ({heads})'.format(tn=x,heads=c))
    db.commit()
    db.close()

db=sqlite3.connect(sql_file)
conn=db.cursor()

#build flatfiles for each condition
for x,n in zip(rel_measures,conditions):
    local_city=rel_cdata.loc[rel_cdata['Measure']==x]
    loc_df=pd.DataFrame()
    for placetrack,c in enumerate(city_ids):
        df=data.loc[data['rPUMA'].isin(city_ids[c])]

        targ=local_city.loc[local_city['CityName']==c]
        df['target']=targ['Data_Value'].mean()
        prev_en=conn.execute('SELECT COUNT (*) FROM {tab}'.format(tab=n)).fetchall()[0][0]
        if prev_en != 0:
            df['entry']=np.arange(prev_en+1,prev_en+1+len(df),1)
            #if existing entries, get the entry val from last one and use that for np.arange for new entry vals
        else:
            df['entry']=np.arange(0,len(df),1)
            #if no exisiting entries init entry val to len of df    
        df.to_sql(n,db,if_exists='append',index=False)
        db.commit()
        print placetrack
db.close()

    
    
#set targ equal to mean Data_Value and use this one value for all of df['target']   
#probably also get the population count stats for stats


















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


