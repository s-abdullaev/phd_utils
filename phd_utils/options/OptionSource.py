# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 21:42:07 2015

@author: Desmond
"""
import pandas as pd
import numpy as np
import scipy
import scipy.stats

class OptionSource(object):
    def __init__(self):
        self.symb='NDX   161216C04320000'
        self.options=pd.read_csv('C:\\MatlabData\\ndx.options.20140101.1231.csv')
        self.rates=pd.read_csv('C:\\MatlabData\\interest_rates_2014.csv')
        self.stock=pd.read_csv('C:\\MatlabData\\ndx.stock.20140101.1231_2.csv')
               
        self.options.columns=[i.strip() for i in self.options.columns]
        self.stock.columns=[i.strip() for i in self.stock.columns]
        self.rates.date=pd.to_datetime(self.rates.date, format='%d/%m/%Y', coerce=True)
        self.stock.date=pd.to_datetime(self.stock.date, format='%d/%m/%Y', coerce=True)
        
    def get(self):
        df=self.options
        callDf=df[df['symbol']==self.symb]
        callDf.date=pd.to_datetime(callDf.date)
                
        exp=pd.to_datetime(callDf.expiration.iget(0))
        
        
        callDf['timeToMat']=(exp-callDf.date).dt.days/365.0
        callDf=pd.merge(callDf, self.rates, on='date')
        callDf.rate=[float(r)/10000.0 for r in callDf.rate]        
        callDf.strike=[float(r) for r in callDf.strike]
        
        callDf=pd.merge(callDf, self.stock.loc[:,['close', 'date']], on='date')
        callDf['blsPrice']=self.blsCall(callDf['close'], callDf['strike'], callDf['rate'], callDf['implied vol'], callDf['timeToMat'])
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

