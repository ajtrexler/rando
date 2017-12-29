# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 10:39:24 2017

@author: adam
"""

import requests
from bs4 import BeautifulSoup
import datetime
import re
import pandas as pd
import time

def checkEDGAR():
    
    url='https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent'
    baseURL='https://www.sec.gov'
    qu=requests.get(url)
    data=qu.text
    meta_cols=['amt','price','transdate','querydate','ticker']
    alldf=pd.DataFrame()
    for tab in data.split('</tr>'):
        if '4</td>' in tab:
            subsoup=BeautifulSoup(tab)
            links=[]
            for l in subsoup.find_all('a'):
                links.append(l.get('href'))
            
            form_qu=requests.get(baseURL+links[1]) #text report to parse.
            f4=form_qu.text
            blah=BeautifulSoup(f4,'html.parser')
            acq_code=blah.find_all('transactionacquireddisposedcode')
            code=re.search('<value>(.)</value>',str(acq_code))
            if code:
                if code.group(1).lower() == 'a':
                    txt=blah.find_all('transactionshares')
                    numsharesraw=re.search('<value>(.+)</value>',str(txt))
                    numshares=int(numsharesraw.group(1))
                    
                    txt=blah.find_all('transactionpricepershare')
                    pricesharesraw=re.search('<value>(.+)</value>',str(txt))
                    priceshares=float(pricesharesraw.group(1))
                    
                    txt=blah.find_all('transactiondate')
                    transdateraw=re.search('<value>(.+)</value>',str(txt))
                    transdate=datetime.datetime.strptime(transdateraw.group(1),'%Y-%m-%d')
                    
                    tickerraw=re.search('<issuertradingsymbol>(.+)</issuertradingsymbol>',str(blah))
                    ticker=tickerraw.group(1)
                    
                    querytime=time.time()
                    filmraw=re.search('FILM NUMBER:\t\t(.+)\n\n',f4)
                    film=int(filmraw.group(1))
                    
                    df=pd.DataFrame(columns=meta_cols,data={'amt':numshares,'price':priceshares,'transdate':transdate,'querydate':querytime,'ticker':ticker},index=[film])
                    if priceshares > 0:
                        alldf=pd.concat([alldf,df])
                else:
                    continue
            else:
                continue
    return alldf

def main():

    savedf=checkEDGAR()
    with open('edgarlogv12.csv','a') as fid:
        savedf.to_csv(fid,header=False)

    
 
#cron for hour execution.   
if __name__ == "__main__":
    main()