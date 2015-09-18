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
import matplotlib.patches as mpatches
import matplotlib.gridspec as mgridspec
import seaborn as sns
import vollib.black_scholes as bls
import vollib.black_scholes.greeks.numerical as greeks

expName='garTraders1'
plotFolder='results/cda_experiments/%s/' % expName
outputPath='plots/cda_experiments/%s_Markets' % expName

optionNames=['atm', 'otm', 'itm']
sns.set_style("whitegrid")

fig=plt.figure(figsize=(10,15))
gs=mgridspec.GridSpec(6,1, height_ratios=[3,1,3,1,3,1])
isShown=False
i=0
for oName in optionNames:
    marketDf=pd.read_excel(plotFolder+oName+'_Market.xls')
    marketDf=marketDf[:-1]
    ax1=plt.subplot(gs[i])
    #plt.gca().set_color_cycle(['blue', 'red'])
    blsPrices, =ax1.plot(marketDf.index, marketDf['BLSPrice'], color='blue', label='Black-Scholes Price')
    daPrices, =ax1.plot(marketDf.index, marketDf['CDAClose'], color='red', label='CDA Close')
    ax1.fill_between(marketDf.index,  marketDf['CDALow'], marketDf['CDAHigh'], facecolor='yellow', alpha=0.4)
#    ax1.fill_between(marketDf.index,  marketDf['rejected_bid_max'], marketDf['rejected_ask_min'], facecolor='orange', alpha=0.6)
#    ax1.fill_between(marketDf.index,  marketDf['rejected_bid_min'], marketDf['rejected_bid_max'], facecolor='yellow', alpha=0.4)
    
    acceptedOrders=mpatches.Patch(color='yellow', label='CDA Low-High')
    volumePatch=mpatches.Patch(color='gray', label='Traded Volume')
#    effErrPatch=mpatches.Patch(color='b', label='Rejected Efficient Trades')
    
    plt.setp(ax1.get_xticklabels(), visible=False)
    ax1.grid(True)
    
    ax1.set_xlim([0, marketDf.index[-1]])
    ax1.set_title(oName.upper() +' Option Prices until Expiration Date', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Option Prices', fontsize=14, fontweight='bold')
    if not isShown:
        ax1.legend(loc='upper right', frameon=True, framealpha=0.7,  fontsize=12, handles=[blsPrices, daPrices, acceptedOrders])
    i+=1

    ax2=plt.subplot(gs[i])
#    vols=np.row_stack((marketDf['Volume'], marketDf['Volume']*(1+marketDf['EffErr'])))
    ax2.fill_between(marketDf.index, 0, marketDf['Volume'], facecolor='gray', alpha=.6)
  #  ax2.fill_between(marketDf.index, vols[0,:], vols[1,:], facecolor='b')
    
    ax2.set_xlim([0, marketDf.index[-1]])
    
    ax2.set_ylabel('Volume', fontsize=14, fontweight='bold')
    plt.setp(ax2.get_xticklabels(), visible=False)
    if i==5:
        ax2.set_xlabel('Time', fontsize=14, fontweight='bold')
        plt.setp(ax2.get_xticklabels(), visible=True)
    isShown=True
    i+=1

plt.tight_layout()
fig.savefig(outputPath, dpi=300)

#def plotLin(filename, fields):
#    df=pd.read_excel('results/da_experiments/mixedMoreRiskAverseTraders1/'+filename)
#    df.plot(y=fields)
#
#def plotHist(filename, fields):
#    df=pd.read_excel('results/da_experiments/mixedMoreRiskAverseTraders1/'+filename)
#    df.plot(fields, kind='hist')

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