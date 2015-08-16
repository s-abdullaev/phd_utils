# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 05:26:19 2015

@author: Desmond
"""
from __future__ import division
import numpy as np
import pandas as pd
import copy
from phd_utils.options.EuropeanOption import *
from phd_utils.assetPricing.models import *
from phd_utils.optionPricing.models import *
from phd_utils.optionPricing.qntyModels import *
from phd_utils.mechanisms.direct_models import *
from phd_utils.mechanisms.experiment import *
from phd_utils.tradingAlgos.DATrader import *
import scipy.optimize as optim
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
import vollib.black_scholes as bls
import vollib.black_scholes.greeks.numerical as greeks

def plotLin(filename, fields):
    df=pd.read_excel('results/da_experiments/mixedMoreRiskAverseTraders1/'+filename)
    df.plot(y=fields)

def plotHist(filename, fields):
    df=pd.read_excel('results/da_experiments/mixedMoreRiskAverseTraders1/'+filename)
    df.plot(fields, kind='hist')


#r=0.0007
#sigma=0.0089
#arrRate=0.8
#jumpMu=-0.004
#jumpSigma=0.0083
#S0=3563.57
#K=3563.57
#eps=50
#T=1
#
#def impVol(price, strike):
#    def optPrice(curVol):
#        if curVol<0: return 1000
#        return (price-bls.black_scholes('c', S0, strike, T, r, curVol))**2
#    
#    return optim.fmin(optPrice, sigma, xtol=0.01)
#
#def blsPrice(strike):
#    return bls.black_scholes('c', S0, strike, T, r, sigma)  
#    
#
#strikes=np.arange(3500.0,3700.0, 10.0)
#vols=[impVol(blsPrice(s), s) for s in strikes]
#plt.plot(strikes, vols)