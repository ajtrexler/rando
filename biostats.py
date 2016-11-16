# -*- coding: utf-8 -*-
"""
Created on Sun Nov 13 12:54:01 2016

@author: adam
"""
import os
from datetime import datetime
import datetime as dt
import numpy as np
import pandas as pd
import gpxpy as gpx
import re
import matplotlib.pyplot as plt
import seaborn as sea
sea.set_style('white')


#define dir for HRV data files
bio_data='/home/adam/scripts/datasets/bio'
strava_data='/home/adam/scripts/datasets/strava'

def hrv_data(place):

    dates=[]
    beats=[]
    avg_interval=[]
    sdnn=[]
    rmssd=[]
    sdsd=[]
    am_only=[]
    for x in os.listdir(place):
        #parse datetime from filename, if filename begins with 2
        if x.find('2')==0:
            tofread=datetime.strptime(x.replace('.txt',''),'%Y-%m-%d %H-%M-%S')
            dates.append(tofread)
            with open(x,'r') as myfile:
                q=myfile.readlines()
                local_data=[float(e) for e in q]
                ssd=[]
                for i in np.arange(0,(len(local_data)-1)):
                    ssd.append(local_data[i]-local_data[i+1])
                rmssd.append(np.sqrt(np.mean(np.square(ssd))))
                sdsd.append(np.std(ssd))
                avg_interval.append(np.mean(local_data))
                sdnn.append(np.std(local_data))
                #parse if I think this was a 2min30s reading in AM
                if (tofread.hour<7) & (len(q)>80):
                    beats.append(len(q)/2.5)
                    am_only.append(np.sqrt(np.mean(np.square(ssd))))
                elif (tofread.hour>20) & (len(q)<80):
                    beats.append(len(q))
                    am_only.append(np.nan)
                else:
                    beats.append(np.nan)
                    am_only.append(np.nan)

                myfile.close()         
    cols=['beats','avg_interval','sdnn','rmssd','sdsd','am_only']
    output=pd.DataFrame(index=dates,data={'beats':beats,'avg_interval':avg_interval,'sdnn':sdnn,'rmssd':rmssd,'sdsd':sdsd,'am_only':am_only})
    return output

def parse_gpx(start,end,place):
    dates=[]
    mileage=[]
    duration=[]
    elev=[]
    pace=[]
    for x in os.listdir(place):
        g=re.match('\d{8}',x)
        if (g) and (x.find('Run')>0):
            togpx=datetime.strptime(g.group(0),'%Y%m%d')
            if togpx>start and togpx<end:
                with open(x,'r') as gpxfile:
                    current=gpx.parse(gpxfile)
                gpxfile.close()
                if current.get_duration()>0:
                    dates.append(togpx)
                    duration.append(current.get_duration()/60)
                    mileage.append((current.length_2d()/1000)*0.6214)
                    p=(current.get_duration()/60)/((current.length_2d()/1000)*0.6214)
                    pace.append(p)
                    if current.get_elevation_extremes()[0]!=None:
                        elev.append(current.get_elevation_extremes()[1]-current.get_elevation_extremes()[0])
    bio_output=pd.DataFrame(index=dates,data={'duration':duration,'mileage':mileage,'elev':elev,'pace':pace})
    return bio_output

#want to make func to build a combo df for plotting purposes, combining strava features and hrv features and time binning into single days.
def plot_corr(hr,en):
    hr.dropna(inplace=True)
    en.dropna(inplace=True)
    dates=[]
    hr_vals=[]
    endo_vals=[]
    for x in hr.index:
        l_com=[((x-y<dt.timedelta(days=1)) and (x-y>dt.timedelta(days=0))) for y in en.index]
        dates.append(x.date())
        hr_vals.append(hr[x])
        endo_vals.append(np.sum(en[l_com]))
    hr_vals=(hr_vals-np.mean(hr_vals))-np.std(hr_vals)
    endo_vals=(endo_vals-np.mean(endo_vals))-np.std(endo_vals)
    combo=pd.DataFrame(index=dates,data={'hrv':hr_vals,'endurance':endo_vals})
    return combo


#test effect of previous day training on heartrate params.
#inputs: endurance parameter, HRV param.
#outputs: new df, organized with each row as an endurance stat and +1 and +2 day HRV stats
def prev_day(hr,en):
    hr.dropna(inplace=True)
    en.dropna(inplace=True)
    date_idx=[]
    endo=[]
    p1_hrv=[]
    p2_hrv=[]
    #deal with duplicates in en, double-workout days.
    for e in en.index:
        dup_com=[((e-ee<dt.timedelta(days=1)) and (e-ee>=dt.timedelta(days=0))) for ee in en.index]
        en_agg=np.sum(en[dup_com])
        if np.sum(dup_com)>=2:
            en.drop(e,inplace=True)
            en.loc[e]=en_agg
    for x in en.index:
        p1_com=[((x-y<dt.timedelta(days=1)) and (x-y>dt.timedelta(days=0))) for y in hr.index]
        p2_com=[((x-y<dt.timedelta(days=2)) and (x-y>dt.timedelta(days=1))) for y in hr.index]
        if x.date() not in date_idx:
            date_idx.append(x.date())
            endo.append(en[x])
            p1_hrv.append(np.mean(hr[p1_com]))
            p2_hrv.append(np.mean(hr[p2_com]))
    retvals=pd.DataFrame(index=date_idx,data={'endurance':endo,'d1_hrv':p1_hrv,'d2_hrv':p2_hrv})
    return retvals   
    
    
#func similar to prev_day, above, but instead of looking forward from each endurance activity it sums
#backwards from each HRV reading for defined num of days to measure cumulative mileage, duration, or elev
#not meant for pace.
def prev_workload(hr,en,n): 
    hr.dropna(inplace=True)
    en.dropna(inplace=True)
    date_idx=[]
    endo_load=[]
    hrv_stat=[]
    for h in hr.index:
        load_com=[((x-h<dt.timedelta(days=n)) and (x-h>dt.timedelta(days=0))) for x in en.index]
        endo_load.append(np.sum(en[load_com]))
        hrv_stat.append(hr[h])
        if h.date() not in date_idx:
            date_idx.append(h.date())
        else:
            date_idx.append(h.date()+dt.timedelta(hours=2))
    retvals=pd.DataFrame(index=date_idx,data={'hrv':hrv_stat,'workload':endo_load})
    return retvals

               
#define time range to parse GPX data over.
end=datetime.now()        
start=datetime.strptime('2016815','%Y%m%d')
my_hrv=hrv_data(bio_data)  
my_strava=parse_gpx(start,end,strava_data) 



#build df to look at HRV stats correlation with all the endurance parameters 1 and 2 day post-exercise.
#calculate pearson's correlation coefficient to calc the relation between these.
d1_trend_df=pd.DataFrame(index=my_strava.columns.values,columns=my_hrv.columns.values)
d2_trend_df=pd.DataFrame(index=my_strava.columns.values,columns=my_hrv.columns.values)
for y in my_strava:
    for v in my_hrv:
        b=prev_day(my_hrv[v],my_strava[y])
        bc=b.corr()
        d1_trend_df.loc[y,v]=bc.loc['d1_hrv','endurance']
        d2_trend_df.loc[y,v]=bc.loc['d2_hrv','endurance']


ax1=d1_trend_df.plot(kind='bar',grid=True,figsize=(10,10),title='one day post exercise correlations of HRV stats with endurance stats')
fig1=ax1.get_figure()
fig1.savefig('HRV_fig1.png')

ax2=d2_trend_df.plot(kind='bar',grid=True,figsize=(10,10),title='two day post exercise correlations of HRV stats with endurance stats')
fig2=ax2.get_figure()
fig2.savefig('HRV_fig2.png')


#use plot_corr to build aligned df of one HRV and one endurance stat for easy plotting and visualization.
blah=plot_corr(my_hrv['rmssd'],my_strava['mileage'])
ax3=blah.plot(rot=90,figsize=(10,10),title='normalized HRV and endurance data')
fig3=ax.get_figure()
fig3.savefig('HRV_fig3.png')

#use prev_workload to look at overall effects of training load on HRV params.
qlah=prev_workload(my_hrv['rmssd'],my_strava['duration'],7)   


ax4=sea.jointplot(x=qlah['hrv'],y=qlah['workload'])
ax4.savefig('HRV_fig4.png')

     

