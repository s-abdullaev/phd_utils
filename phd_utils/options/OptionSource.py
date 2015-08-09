# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 21:42:07 2015

@author: Desmond
"""
from __future__ import division
import pandas as pd
import numpy as np
import scipy
import scipy.stats

class OptionSource(object):
    def __init__(self):
        self.options=pd.read_csv('../../data/ndx.options.20140101.1231.csv', parse_dates=['date', ' expiration'])
        self.rates=pd.read_excel('../../data/interest_rates_2014_daily.xlsx')
        self.stock=pd.read_csv('../../data/ndx.stock.20140101.1231_2.csv', parse_dates=['date'])
               
        self.options.columns=[i.strip() for i in self.options.columns]
        self.stock.columns=[i.strip() for i in self.stock.columns]
        self.rates.columns=[i.lower() for i in self.rates.columns]
        
    def get(self, symb='NDX   161216C04320000'):
        df=self.options
        callDf=df[df['put/call']=='C']
        if symb:
            callDf=callDf[callDf['symbol']==symb]
                
        callDf['timeToMat']=(callDf.expiration-callDf.date).dt.days/365
        callDf=pd.merge(callDf, self.rates, on='date')
        callDf['rate']=callDf['1 yr'].apply(lambda x: float(x)/100)
        callDf['strike']=callDf['strike'].apply(lambda x: float(x))
        
        callDf=pd.merge(callDf, self.stock[['close', 'date']], on='date')
        callDf['blsPrice']=self.blsCall(callDf['close'], callDf['strike'], callDf['rate'], callDf['implied vol'], callDf['timeToMat'])
        callDf['bid_bls_ratio']=callDf['bid']/callDf['blsPrice']
        callDf['ask_bls_ratio']=callDf['ask']/callDf['blsPrice']
#        callDf.index=callDf.date

        return callDf

    def discount(self, val, r, T):
        return val*np.exp(-r*T)

    def d1(self, S0, K, r, sigma, T):
        return (np.log(S0 / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))

    def d2(self, S0, K, r, sigma, T):
        return (np.log(S0 / K) + (r - sigma**2 / 2) * T) / (sigma * np.sqrt(T))

    def blsCall(self, S0, K, r, sigma, T):
        return S0 * scipy.stats.norm.cdf(self.d1(S0, K, r, sigma, T)) - scipy.stats.norm.cdf(self.d2(S0, K, r, sigma, T))*self.discount(K, r, T)

    def blsPut(self, S0, K, r, sigma, T):
        return self.discount(K,r,T) * scipy.stats.norm.cdf(-self.d2(S0, K, r, sigma, T))-S0 * scipy.stats.norm.cdf(-self.d1(S0, K, r, sigma, T))

