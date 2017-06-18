# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 18:54:42 2017

@author: adam
"""

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap as Basemap
from matplotlib.colors import rgb2hex
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection 
import seaborn as sea

bls_url='https://api.bls.gov/publicAPI/v2/timeseries/data/'


state_table=pd.read_csv('bls_states.csv')
u_tables=pd.read_csv('bls_seriesids.csv')
unemploy=u_tables.loc[2,'seriesid']
#get the tables
real_unemploy=u_tables.loc[5,'seriesid']
#series getting unemployment rates by state over the years.


def fetch_series(x):
    if isinstance(x,list)==False:
        params={'seriesid':[x],'startyear':'2007','endyear':'2017','catalog':True,'registrationkey':'1899bedee3654c8793f9a80fcb68c0a7'}
    else:
        params={'seriesid':x,'startyear':'2007','endyear':'2017','catalog':True,'registrationkey':'1899bedee3654c8793f9a80fcb68c0a7'}

    f=requests.post(url=bls_url,json=params)
    data=f.json()['Results']['series']
    if len(data)>1:
        con_df=pd.DataFrame()
        for d in data:
            if d['data']!= []:
                numbers=d['data']
                values=[]
                idx=[]
                for n in numbers:
                    values.append(float(n['value']))
                    idx.append(str(n['periodName'])+str(n['year']))
                
                df=pd.DataFrame(index=idx,data=values,columns=[d['catalog']['area']])
                con_df=pd.concat([con_df,df],1)
            else:
                continue
        return con_df
        
    else:
        d=data[0]
        if d['data']!= []:
            numbers=d['data']
            values=[]
            idx=[]
            for n in numbers:
                values.append(float(n['value']))
                idx.append(str(n['periodName'])+str(n['year']))
            
            return pd.DataFrame(index=idx,data=values)
        else:
            return 'error on json read' 


seriesid=[]
for s in state_table['state_code']:
    if s<=9:
        seriesid.append('LASST{x}0000000000003'.format(x='0'+str(s)))  
    else:
        seriesid.append('LASST{x}0000000000003'.format(x=str(s)))

perstate_df=pd.concat([fetch_series(seriesid[0:25]),fetch_series(seriesid[25:])],1)

perstate_df=perstate_df.iloc[::-1]

u3df=fetch_series(unemploy)[::-1]
u6df=fetch_series(real_unemploy)[::-1]
udf=pd.concat([u3df,u6df],1)
udf.columns=['official','real']

q1=plt.figure(figsize=[5,5])
q1=udf.plot()
plt.suptitle('The real and official unemployment rates over ten years')
plt.xticks(rotation=45)
plt.ylabel('unemployment rate')
plt.savefig('unemploy_fig1.png')

q2=plt.figure(figsize=[5,5])
q2=udf.divide(udf.iloc[1,:]).plot()
plt.suptitle('Normalized unemployment rates over ten years')
plt.xticks(rotation=45)
plt.ylabel('normalized unemployment (AU)')
plt.savefig('unemploy_fig2.png')


perstate_df['West Virginia'].plot()    


blah=perstate_df.apply(lambda x:max(x))  
blah_delta=perstate_df.apply(lambda x: max(x)-x.loc['January2007'])
blah_recovery=perstate_df.apply(lambda x: ((max(x)-x.loc['March2017'])/ (max(x)-x.loc['January2007']))-1)

# Lambert Conformal map of lower 48 states.
m = Basemap(llcrnrlon=-119,llcrnrlat=22,urcrnrlon=-64,urcrnrlat=49,
        projection='lcc',lat_1=33,lat_2=45,lon_0=-95,width=10,height=5)
# draw state boundaries.
# data from U.S Census Bureau
# cb_2016_us_state_5m, lower 48 shape files.
m.readshapefile('states','states',drawbounds=True)

colors={}
states=[]
cmap=plt.cm.rainbow
blah_plot=blah_recovery
cmax=float(max(blah_plot))

segs_to_plot=[]
for shapedict,seg in zip(m.states_info,m.states):
    statename=shapedict['STATE_NAME']
    if statename not in ['United States Virgin Islands','Commonwealth of the Northern Mariana Islands','Guam','American Samoa','District of Columbia','Puerto Rico','Alaska','Hawaii']:
        segs_to_plot.append(seg)
        colors[statename]=cmap(blah_plot.loc[statename]/cmax)[:3]
        states.append(statename)

# cycle through state names, color each one.
ax = plt.gca() # get current axes instance
patches=[]
for nshape,seg in enumerate(segs_to_plot):
    # skip DC and Puerto Rico.
    if states[nshape] not in ['United States Virgin Islands','Commonwealth of the Northern Mariana Islands','Guam','American Samoa','District of Columbia','Puerto Rico','Alaska','Hawaii']:
        color = rgb2hex(colors[states[nshape]]) 
        poly = Polygon(seg,facecolor=color,edgecolor=color)
        ax.add_patch(poly)
        patches.append(poly)
p=PatchCollection(patches,cmap=cmap)
p.set_array(np.array(blah_plot.values))
plt.colorbar(p)
plt.title('Unemployment increase Jan2007 to height of financial crisis')
plt.savefig('unemploy_fig3.png')

q4=plt.figure()
q4=blah_recovery.plot(kind='bar')
plt.suptitle('recovery score by state in unemployment values')
plt.ylabel('normalized recovery score')
plt.savefig('unemploy_fig4.png')
