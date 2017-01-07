# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 20:51:05 2017

@author: adam
"""
import pandas as pd
from thinkbayes import Suite
import numpy as np
import thinkbayes
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import scipy
import thinkplot


rawdata=pd.read_csv('grammys.csv')
b_data=[0.5,0,1,0,0,0.6,0,0,0.25,0.16,0,0.83,0.5,0.4,0]
rawbin_data=pd.read_csv('beyonce_grammys.csv')
bin_data=zip(rawbin_data['noms'],rawbin_data['awards'])

f=plt.figure()
rawdata['award/nom'].plot(kind='hist')
plt.xlabel('award/nom')
plt.title('histogram to awards/nomination past winners of Album of Year')
plt.savefig('grammy_fig1')

n = len(data)
mean_grams = sum(data)/n                   
sigma_grams = np.std(data)    

#call it a gaussian with mean and sigma given above.
   
counts,edges=np.histogram(data)
class binom_grammy(Suite):
    def __init__(self,name=''):
        pmf=thinkbayes.MakeGaussianPmf(mean_grams,sigma_grams,3,20)
        thinkbayes.Suite.__init__(self,pmf,name=name)
    
    def Likelihood(self,data,hypo):
        if hypo < 0:
            return 0.00001
        else:
            
            k=data[0]
            n=data[1]
            like=thinkbayes.EvalBinomialPmf(k,n,hypo)
            if like == 0:
                return 0.00001
            else:
                return like
            
def MakePoissonPmf_mod1(lam, high, step):
    """Makes a PMF discrete approx to a Poisson distribution.

    lam: parameter lambda in events per unit time
    high: upper bound of the Pmf

    returns: normalized Pmf
    """
    pmf = thinkbayes.Pmf()
    for k in np.arange(0, high, step):
        print k
        p = thinkbayes.EvalPoissonPmf(k, lam)
        pmf.Set(k, p)
    pmf.Normalize()
    return pmf
    
    
def makegramPmf(suite):
    metapmf=thinkbayes.Pmf()
    
    for na,prob in model.Items():
        pmf=MakePoissonPmf_mod1(na*9,9,1)
        metapmf.Set(pmf,prob)
    mix=thinkbayes.MakeMixture(metapmf)
    return mix
    
    
class hyper_grammy(Suite):
    def __init__(self,name=''):
        pmf=thinkbayes.MakeGaussianPmf(mean_grams,sigma_grams,4,20)
        thinkbayes.Suite.__init__(self,pmf,name=name)
    
    def Likelihood(self,data,hypo):
        '''
        compute likelihood using hypergeometric dist.
        M= noms, total awards possible
        n= hypo # awards in noms, given hypo award/nom
        N= awards, data from actor
        '''
        if hypo < 0:
            return 0.00001
        else:
            M=data[0]
            N=data[1]
            n=round(hypo*M)
            
            like=scipy.stats.hypergeom.pmf(N,M,n,N)
            print like
            if like == 0:
                return 0.00001
            else:
                return like   

            

        
        
    
model=binom_grammy('beyonce')
model.UpdateSet(bin_data)      
grammys=makegramPmf(model)
thinkplot.plot(model)

model_h=hyper_grammy('beyonce')
model_h.UpdateSet(bin_data)
for x in bin_data:
    
    model_h.Update(x)
    thinkplot.plot(model_h)
    
grammy_hyper=makegramPmf(model_h)
grammy_hyper.Mean()
thinkplot.plot(grammy_hyper)


q=[x[1] for x in model.Items()]
plt.plot(sorted(q))


    

