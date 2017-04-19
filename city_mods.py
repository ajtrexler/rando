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


conditions=['binge','prevent','nosleep']   
sql_file='cityhealth_demo.sqlite'
db=sqlite3.connect(sql_file)
conn=db.cursor()

data=pd.read_sql('SELECT * from {x}'.format(x=conditions[1]),db)
short=data[1:100]

    
meta=pd.DataFrame(columns=short.columns)
for x in np.unique(data['rPUMA']):
    subset=data.loc[data['rPUMA']==x]
    m=subset.mean().to_frame().transpose()
    meta=pd.concat([meta,m],ignore_index=True)

meta.drop(['rPUMA','ST','PUMA','entry','ADJINC'],1,inplace=True)
#ab_targets=np.unique(data['target'].values)
#plt.hist(ab_targets)
#subset=data.loc[data['target']>50]
data.drop(['rPUMA','ST','PUMA','entry','ADJINC'],1,inplace=True)
targets=meta['target']
metascale=ppp.StandardScaler().fit_transform(meta.drop('target',1))

train,test,train_y,test_y=skcv.train_test_split(metascale,targets,train_size=0.2)

model=sklearn.svm.LinearSVR(C=1).fit(train,train_y)
pred=model.predict(test)
print met.r2_score(test_y,pred)

model=linmod.SGDRegressor()


