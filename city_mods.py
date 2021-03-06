# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 20:38:49 2017

@author: adam
"""

import pandas as pd
import numpy as np
import time
import os
import re
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sea
import sklearn.ensemble as ens
import sklearn.preprocessing as ppp
import sklearn.cross_validation as skcv
import sklearn.metrics as met
import sklearn.linear_model as linmod
import sklearn.svm
import seaborn as sea
import matplotlib.pyplot as plt


conditions=['binge','prevent','nosleep']   
sql_file='cityhealth_demo.sqlite'
db=sqlite3.connect(sql_file)
conn=db.cursor()

data=pd.read_sql('SELECT * from {x}'.format(x=conditions[2]),db)
short=data[1:100]


    
meta=pd.DataFrame()
meta_cats=pd.DataFrame()
#metavar=pd.DataFrame()
#noncat_feats=['PINCP','rPUMA','ADJINC','ST','PUMA','entry','target','SEMP','AGEP']
#q=[x for x in data.columns.values if x not in noncat_feats]
#ohe=pd.DataFrame()
#encoder=ppp.OneHotEncoder().fit(data[q]+1)

bin_es={}
cat_feats=['AGEP','ANC1P','ANC2P']
for f in cat_feats:
    throw,bin_es[f]=np.histogram(data[f].values,bins=10)

for x in np.unique(data['rPUMA']):
    subset=data.loc[data['rPUMA']==x]
    m=subset.mean().to_frame().transpose()
    m['rPUMA']=subset.iloc[1,-3]
    meta=pd.concat([meta,m],ignore_index=True)
    catfeatsdf=pd.DataFrame()
    for f in cat_feats:
        subcount,throw=np.histogram(subset[f],bins=bin_es[f])
        catfeatsdf=pd.concat([catfeatsdf,pd.DataFrame(data=subcount).T],axis=1)
    m=pd.concat([m,catfeatsdf],axis=1)
    #s=subset.std().to_frame().transpose()
    meta_cats=pd.concat([meta_cats,m],ignore_index=True)

    #m.drop(['target','ST','PUMA','entry','ADJINC'],1,inplace=True)
    #s.drop(['target','ST','PUMA','entry','ADJINC'],1,inplace=True)
    #enc_subset=encoder.transform(subset[q]+1)
    #ohe_toadd=pd.DataFrame(enc_subset.toarray()).sum().to_frame().T
    #toadd=pd.DataFrame(data=np.hstack((m,s)))
    #metavar=pd.concat([metavar,toadd],ignore_index=True)
    #ohe=pd.concat([ohe,ohe_toadd])

#prep data
dataset=meta_cats
dataset.drop(['rPUMA','ST','PUMA','entry','ADJINC'],1,inplace=True)
targets=dataset['target']
metascale=ppp.StandardScaler().fit_transform(dataset.drop('target',1))


nest=50
basil=sklearn.svm.LinearSVR()
kf=sklearn.model_selection.KFold(n_splits=5)
err=[]
for train_idx,test_idx in kf.split(metascale):
    train=metascale[train_idx,:]
    train_y=meta.loc[train_idx,'target']
    test=metascale[test_idx,:]
    test_y=meta.loc[test_idx,'target']
    model=ens.BaggingRegressor(n_estimators=nest).fit(train,train_y)
    pred=model.predict(test)
    err.append(met.mean_squared_error(test_y,pred))
print np.round(np.mean(err),decimals=3),'average mean squared error'
    
#train,test,train_y,test_y=skcv.train_test_split(metascale,targets,train_size=0.2)



ax=pd.Series(model.feature_importances_).plot(kind='bar')
ax.set_xlabel(list(meta.columns))



sea.jointplot(x='ANC2P',y='target',data=meta)

plt.plot(model.feature_importances_)
allfeats=list(meta.columns.values)
zip(model.feature_importances_,allfeats)
plt.xticks(allfeats)

for x in meta:#meta.drop(['target','rPUMA','ST','PUMA','entry','ADJINC'],1):
    print x,np.corrcoef(meta[x].values,meta['target'].values)[1,0]
sea.jointplot(data=meta,x='PINCP',y='target')    

focusgroup=meta.loc[meta['target']>23]
hneg=['SEMP','COW']
hpos=['ANC1P','MAR']
neut=['ENG','AGEP']



invdata=data.loc[data['rPUMA']=='26_3212']
#get full dataset stats on ANC1P and watever else want to compare.
#then compare this to rPUMA's where the target of interest
#select variables to focus on, likely a high pos, high neg, and no corr control.

#map to show where these locales are.  do they cluster in cities?
name_table=pd.read_table('/home/adam/scripts/datasets/2010_PUMA_Names.txt',delimiter=',')
state_table=pd.read_csv('/home/adam/scripts/datasets/puma_state_id.csv')

def p_state_table(x):
    r=re.search('/(\w{2})',x)
    if r:
        return r.group(1)
    else:
        return 'blah'
state_abbr=state_table['Unnamed: 1'].apply(p_state_table)
state_abbr_dict=dict(zip(state_abbr,state_table['State Code']))
lookup={v: k for k,v in state_abbr_dict.iteritems()}


def rpuma_lookup(rp):
    #pass string rp as rPUMA where format is ST_PUMA
    st=lookup[int(rp.split('_')[0])]
    narrow=name_table.loc[name_table['STATEFP']==int(rp.split('_')[0])]
    pum=narrow.loc[narrow['PUMA5CE']==int(rp.split('_')[1])]['PUMA NAME']
    print pum.values,'in',st

for x in focusgroup['rPUMA']:
    rpuma_lookup(x)
    print ' '

def make_box_compare(stat,focus):
    #stat is whatever metric you want to compare, like AGEP or PINCP
    #focus is the list of rPUMAs to compare
    df=pd.DataFrame()
    for x in focus:
        local=data.loc[data['rPUMA']==x,stat].values
        df=pd.concat([pd.DataFrame(local),df],1,ignore_index=True)

    names=list(focus.values)
    names.append('all')
    names.reverse()
    df=pd.concat([(pd.DataFrame(data[stat].sample(n=1000).values)),df],axis=1,ignore_index=True)
    df.columns=names
    
    
    p=sea.violinplot(data=df,whis=1,fliersize=0,inner=None,scale='count')
    #sea.stripplot(data=df.sample(n=100,random_state=1234),edgecolor='black',palette=sea.dark_palette('blue'))
    p.set_ylim([-50000,250000])
    for item in p.get_xticklabels():
        item.set_rotation(45)

#call this in loop for meta creation.  probably want to make that a class or something.
def bin_feature(feat,bin_es):
    #divide feature into
    #bin_es is bin edges, len(bin_es) is the bin number.
    subdata=subset[feat]
    subcount,throw=np.histogram(subdata.values,bins=bin_es)
    return pd.DataFrame(data=subcount)
    
    
    