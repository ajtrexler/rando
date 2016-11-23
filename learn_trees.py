# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 16:12:24 2016
Simple script to build a decision tree on the iris dataset from sklearn. 
Accompanies MacKay's Data Mining book explanation of this protocol.

code every day!

@author: adam
"""

from sklearn.datasets import load_iris
import pandas as pd
import numpy as np


data=load_iris()
df=pd.DataFrame(columns=data['feature_names'],data=data['data'])
targets=data['target']

#for a list of values, bin values with a dictionary and then crudely calculate the entropy
def get_entropy(items):
    item_dict={}
    for x in items:
        if x not in item_dict.keys():
            item_dict[x]=1
        else:
            item_dict[x]+=1
    
    n_items=[float(i)/np.sum(item_dict.values()) for i in item_dict.values()]
    entropy=np.sum([-n*np.log2(n) for n in n_items])
    return entropy

def eval_poss_nodes():
        
        
#calc max entropy from entry dataset targets
dataset_entropy=get_entropy(targets)
#calc data entropy
#midway split on each attribute and calculate gain (total entropy - entropy upon split        
#first calc gain/info over splitting on each of the four features, simply midway split
#calc entropy of child node per split at each of the 4 attributes
#accept max entropy gain as root node, then recurse

ents=[]
for x in df:
    splitpoint=df[x].max()-((df[x].max()-df[x].min())/2)
    node_idx=df[x] <= splitpoint
    #get the target values for True and False daughter nodes
    for x in node_idx.unique():
        print get_entropy(targets[np.where(node_idx==x)])
        
     
    targets[node_idx==True]
    
    ents.append(get_entropy(node_idx))

ents.index(np.min(ents))    
    
    

