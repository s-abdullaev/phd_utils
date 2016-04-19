# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 05:22:32 2015

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
import matplotlib.ticker as mtick
import seaborn as sns
import vollib.black_scholes as bls
import vollib.black_scholes.greeks.numerical as greeks

linAssetPrices=np.linspace(3465, 3665,40)
linTimeToMaturity=np.linspace(1, 0, 40)
times=np.linspace(1,0,365)[:-1]
r=0.0007
sigma=0.0089
arrRate=0.8
jumpMu=-0.004
jumpSigma=0.0083
S0=3563.57
K=3563.57
eps=40
T=1


def getImpVol(prices, assetPrices, times, K, r):
    def optPrice(curVol, price, S0, T):
        return (price-bls.black_scholes('c', S0, K, T, r, curVol))
    sigmas=[]
    for price, S0, T in zip(prices, assetPrices, times):
        sigmas.append(optim.fsolve(optPrice, sigma, args=(price, S0, T))[0])
    pSigmas=np.array(sigmas)    
    countNonZeros=len(pSigmas[pSigmas>0])
#    print sigmas
    return sum(sigmas)/countNonZeros
    
def getImpVol2(prices, assetPrices, times, K, r):
    sigmas=[]
    for price, S0, T in zip(prices, assetPrices, times):
        sigmas.append(bls.implied_volatility.implied_volatility_brent(price,S0, K, T, r, 'c'))
    return np.mean(sigmas)

expName='garTraders'
plotFolder='results/cda_experiments/%s/' % expName
outputPath='plots/cda_experiments/%s_Greeks' % expName

optionNames=['atm', 'otm', 'itm']
sns.set_style("whitegrid")

fig=plt.figure(figsize=(10,15))
gs=mgridspec.GridSpec(4,2)

da_colorcycle=['darkred', 'red', 'salmon']
bls_colorcycle=['navy', 'blue', 'royalblue']

#Cash Distribution
ax=plt.subplot(gs[0])
itm_marketDf=pd.read_excel(plotFolder+'itm_TraderResults.xls')
atm_marketDf=pd.read_excel(plotFolder+'atm_TraderResults.xls')
otm_marketDf=pd.read_excel(plotFolder+'otm_TraderResults.xls')

itm_marketDf=itm_marketDf.join(otm_marketDf, how='left', lsuffix='_itm', rsuffix='_otm')
itm_marketDf=itm_marketDf.join(atm_marketDf, how='left')
ax.hist(itm_marketDf[['trader_cash_itm','trader_cash', 'trader_cash_otm']].values, histtype='bar', normed=1, color=da_colorcycle)
ax.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.e'))
ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.e'))
ax.set_title('Trader Cash Accounts at Option Expiry', fontsize=14, fontweight='bold')
ax.set_xlabel('Cash', fontsize=12, fontweight='bold')
ax.legend(['CDA ITM','CDA ATM', 'CDA OTM'], loc='upper right', frameon=True, framealpha=0.5,  fontsize=12)

#Option Distribution
ax=plt.subplot(gs[1])
ax.hist(itm_marketDf[['trader_options_itm','trader_options', 'trader_options_otm']].values, histtype='bar', normed=1, color=da_colorcycle)
#ax.set_xticks(np.arange(-2e5, 2e5+1, 5e4, dtype='int'))
ax.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.e'))
ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.e'))
ax.set_title('Trader Option Accounts at Option Expiry', fontsize=14, fontweight='bold')
ax.set_xlabel('Num of Options', fontsize=12, fontweight='bold')
ax.legend(['CDA ITM','CDA ATM', 'CDA OTM'], loc='upper right', frameon=True, framealpha=0.5,  fontsize=12)

#DELTA
ax=plt.subplot(gs[2])
itm_marketDf=pd.read_excel(plotFolder+'itm_Market.xls')
atm_marketDf=pd.read_excel(plotFolder+'atm_Market.xls')
otm_marketDf=pd.read_excel(plotFolder+'otm_Market.xls')

itm_marketDf=itm_marketDf[:-1]
atm_marketDf=atm_marketDf[:-1]
otm_marketDf=otm_marketDf[:-1]


itm_impVol=getImpVol(itm_marketDf['CDAHigh'], itm_marketDf['AssetPrice'], times, K-eps, r)
atm_impVol=getImpVol(atm_marketDf['CDAHigh'], atm_marketDf['AssetPrice'], times, K, r)
otm_impVol=getImpVol(otm_marketDf['CDAHigh'], otm_marketDf['AssetPrice'], times, K+eps, r)
otm_impVol=sigma+0.003

deltaDf=pd.DataFrame(np.zeros([len(linAssetPrices), 6]), columns=['DA_Delta_itm', 'DA_Delta', 'DA_Delta_otm','BLS_Delta_itm', 'BLS_Delta', 'BLS_Delta_otm'])
deltaDf['DA_Delta_itm']=[bls.greeks.analytical.delta('c', s, K-eps, 1, r, otm_impVol) for s in linAssetPrices]
deltaDf['DA_Delta']=[bls.greeks.analytical.delta('c', s, K, 1, r, otm_impVol) for s in linAssetPrices]
deltaDf['DA_Delta_otm']=[bls.greeks.analytical.delta('c', s, K+eps, 1, r,  otm_impVol) for s in linAssetPrices]
deltaDf['BLS_Delta_itm']=[bls.greeks.analytical.delta('c', s, K-eps, 1, r, sigma) for s in linAssetPrices]
deltaDf['BLS_Delta']=[bls.greeks.analytical.delta('c', s, K, 1,r, sigma) for s in linAssetPrices]
deltaDf['BLS_Delta_otm']=[bls.greeks.analytical.delta('c', s, K+eps, 1,r, sigma) for s in linAssetPrices]

ax.set_color_cycle(da_colorcycle)
ax.plot(linAssetPrices, 
            deltaDf[['DA_Delta_itm', 'DA_Delta', 'DA_Delta_otm']],
            linewidth=2)
            
ax.set_color_cycle(bls_colorcycle)
ax.plot(linAssetPrices, 
            deltaDf[['BLS_Delta_itm', 'BLS_Delta', 'BLS_Delta_otm']],
            linestyle='--')
ax.set_xlim(linAssetPrices[0], linAssetPrices[39])
ax.set_xlabel('Asset Prices', fontsize=12, fontweight='bold')
ax.set_ylabel('Delta', fontsize=12, fontweight='bold')
ax.set_title('Option Deltas vs Asset Prices', fontsize=14, fontweight='bold')
ax.legend(['CDA ITM',' CDA ATM', 'CDA OTM','BLS ITM','BLS ATM', 'BLS OTM'], loc='lower right', frameon=True, framealpha=0.5,  fontsize=12)
ax.grid(True)
#
##DELTA WITH TIME
ax=plt.subplot(gs[3])

deltaDf=pd.DataFrame(np.zeros([len(linAssetPrices), 6]), columns=['DA_Delta_itm', 'DA_Delta', 'DA_Delta_otm','BLS_Delta_itm', 'BLS_Delta', 'BLS_Delta_otm'])
deltaDf['DA_Delta_itm']=[bls.greeks.analytical.delta('c', S0, K-eps, s, r, otm_impVol) for s in linTimeToMaturity]
deltaDf['DA_Delta']=[bls.greeks.analytical.delta('c', S0, K, s, r, otm_impVol) for s in linTimeToMaturity]
deltaDf['DA_Delta_otm']=[bls.greeks.analytical.delta('c', S0, K+eps, s, r,  otm_impVol) for s in linTimeToMaturity]
deltaDf['BLS_Delta_itm']=[bls.greeks.analytical.delta('c', S0, K-eps, s, r, sigma) for s in linTimeToMaturity]
deltaDf['BLS_Delta']=[bls.greeks.analytical.delta('c', S0, K, s,r, sigma) for s in linTimeToMaturity]
deltaDf['BLS_Delta_otm']=[bls.greeks.analytical.delta('c', S0, K+eps, s,r, sigma) for s in linTimeToMaturity]

ax.set_color_cycle(da_colorcycle)
ax.plot(linTimeToMaturity, 
            deltaDf[['DA_Delta_itm', 'DA_Delta', 'DA_Delta_otm']],
            linewidth=2)
            
ax.set_color_cycle(bls_colorcycle)
ax.plot(linTimeToMaturity, 
            deltaDf[['BLS_Delta_itm', 'BLS_Delta', 'BLS_Delta_otm']],
            linestyle='--')
ax.set_xlim(linTimeToMaturity[0], linTimeToMaturity[39])
ax.set_xlabel('Time to Maturity', fontsize=12, fontweight='bold')
ax.set_ylabel('Delta', fontsize=12, fontweight='bold')
ax.set_title('Option Deltas vs Time to Maturity', fontsize=14, fontweight='bold')
ax.legend(['CDA ITM',' CDA ATM', 'CDA OTM','BLS ITM','BLS ATM', 'BLS OTM'], loc='lower right', frameon=True, framealpha=0.5,  fontsize=12)
ax.grid(True)
#
##GAMMA
ax=plt.subplot(gs[4])

deltaDf=pd.DataFrame(np.zeros([len(linAssetPrices), 6]), columns=['DA_Gamma_itm', 'DA_Gamma', 'DA_Gamma_otm','BLS_Gamma_itm', 'BLS_Gamma', 'BLS_Gamma_otm'])
deltaDf['DA_Gamma_itm']=[bls.greeks.analytical.gamma('c', s, K-eps, 1, r, otm_impVol) for s in linAssetPrices]
deltaDf['DA_Gamma']=[bls.greeks.analytical.gamma('c', s, K, 1, r, otm_impVol) for s in linAssetPrices]
deltaDf['DA_Gamma_otm']=[bls.greeks.analytical.gamma('c', s, K+eps, 1, r,  otm_impVol) for s in linAssetPrices]
deltaDf['BLS_Gamma_itm']=[bls.greeks.analytical.gamma('c', s, K-eps, 1, r, sigma) for s in linAssetPrices]
deltaDf['BLS_Gamma']=[bls.greeks.analytical.gamma('c', s, K, 1,r, sigma) for s in linAssetPrices]
deltaDf['BLS_Gamma_otm']=[bls.greeks.analytical.gamma('c', s, K+eps, 1,r, sigma) for s in linAssetPrices]

ax.set_color_cycle(da_colorcycle)
ax.plot(linAssetPrices, 
            deltaDf[['DA_Gamma_itm', 'DA_Gamma', 'DA_Gamma_otm']],
            linewidth=2)
            
ax.set_color_cycle(bls_colorcycle)
ax.plot(linAssetPrices, 
            deltaDf[['BLS_Gamma_itm', 'BLS_Gamma', 'BLS_Gamma_otm']],
            linestyle='--')
ax.set_xlim(linAssetPrices[0], linAssetPrices[39])
ax.set_xlabel('Asset Prices', fontsize=12, fontweight='bold')
ax.set_ylabel('Gamma', fontsize=12, fontweight='bold')
ax.set_title('Option Gammas vs Asset Prices', fontsize=14, fontweight='bold')
ax.legend(['CDA ITM',' CDA ATM', 'CDA OTM','BLS ITM','BLS ATM', 'BLS OTM'], loc='lower right', frameon=True, framealpha=0.5,  fontsize=12)
ax.grid(True)

##GAMMA WITH TIME
ax=plt.subplot(gs[5])

deltaDf=pd.DataFrame(np.zeros([len(linAssetPrices), 6]), columns=['DA_Gamma_itm', 'DA_Gamma', 'DA_Gamma_otm','BLS_Gamma_itm', 'BLS_Gamma', 'BLS_Gamma_otm'])
deltaDf['DA_Gamma_itm']=[bls.greeks.analytical.gamma('c', S0, K-eps, s, r, otm_impVol) for s in linTimeToMaturity]
deltaDf['DA_Gamma']=[bls.greeks.analytical.gamma('c', S0, K, s, r, otm_impVol) for s in linTimeToMaturity]
deltaDf['DA_Gamma_otm']=[bls.greeks.analytical.gamma('c', S0, K+eps, s, r,  otm_impVol) for s in linTimeToMaturity]
deltaDf['BLS_Gamma_itm']=[bls.greeks.analytical.gamma('c', S0, K-eps, s, r, sigma) for s in linTimeToMaturity]
deltaDf['BLS_Gamma']=[bls.greeks.analytical.gamma('c', S0, K, s,r, sigma) for s in linTimeToMaturity]
deltaDf['BLS_Delta_otm']=[bls.greeks.analytical.gamma('c', S0, K+eps, s,r, sigma) for s in linTimeToMaturity]

ax.set_color_cycle(da_colorcycle)
ax.plot(linTimeToMaturity, 
            deltaDf[['DA_Gamma_itm', 'DA_Gamma', 'DA_Gamma_otm']],
            linewidth=2)
            
ax.set_color_cycle(bls_colorcycle)
ax.plot(linTimeToMaturity, 
            deltaDf[['BLS_Gamma_itm', 'BLS_Gamma', 'BLS_Gamma_otm']],
            linestyle='--')
ax.set_xlim(linTimeToMaturity[0], linTimeToMaturity[39])
ax.set_xlabel('Time to Maturity', fontsize=12, fontweight='bold')
ax.set_ylabel('Gamma', fontsize=12, fontweight='bold')
ax.set_title('Option Gammas vs Time to Maturity', fontsize=14, fontweight='bold')
ax.legend(['CDA ITM','CDA ATM', 'CDA OTM','BLS ITM','BLS ATM', 'BLS OTM'], loc='upper right', frameon=True, framealpha=0.5,  fontsize=12)
ax.grid(True)
#
##THETA
ax=plt.subplot(gs[6])

deltaDf=pd.DataFrame(np.zeros([len(linAssetPrices), 6]), columns=['DA_Theta_itm', 'DA_Theta', 'DA_Theta_otm','BLS_Theta_itm', 'BLS_Theta', 'BLS_Theta_otm'])
deltaDf['DA_Theta_itm']=[bls.greeks.analytical.theta('c', s, K-eps, 1, r, otm_impVol) for s in linAssetPrices]
deltaDf['DA_Theta']=[bls.greeks.analytical.theta('c', s, K, 1, r, otm_impVol) for s in linAssetPrices]
deltaDf['DA_Theta_otm']=[bls.greeks.analytical.theta('c', s, K+eps, 1, r,  otm_impVol) for s in linAssetPrices]
deltaDf['BLS_Theta_itm']=[bls.greeks.analytical.theta('c', s, K-eps, 1, r, sigma) for s in linAssetPrices]
deltaDf['BLS_Theta']=[bls.greeks.analytical.theta('c', s, K, 1,r, sigma) for s in linAssetPrices]
deltaDf['BLS_Theta_otm']=[bls.greeks.analytical.theta('c', s, K+eps, 1,r, sigma) for s in linAssetPrices]

ax.set_color_cycle(da_colorcycle)
ax.plot(linAssetPrices, 
            deltaDf[['DA_Theta_itm', 'DA_Theta', 'DA_Theta_otm']],
            linewidth=2)
            
ax.set_color_cycle(bls_colorcycle)
ax.plot(linAssetPrices, 
            deltaDf[['BLS_Theta_itm', 'BLS_Theta', 'BLS_Theta_otm']],
            linestyle='--')
ax.set_xlim(linAssetPrices[0], linAssetPrices[39])
ax.set_xlabel('Asset Prices', fontsize=12, fontweight='bold')
ax.set_ylabel('Theta', fontsize=12, fontweight='bold')
ax.set_title('Option Thetas vs Asset Prices', fontsize=14, fontweight='bold')
ax.legend(['CDA ITM',' CDA ATM', 'CDA OTM','BLS ITM','BLS ATM', 'BLS OTM'], loc='lower right', frameon=True, framealpha=0.5,  fontsize=12)
ax.grid(True)
#
##THETA WITH TIME
ax=plt.subplot(gs[7])

deltaDf=pd.DataFrame(np.zeros([len(linAssetPrices), 6]), columns=['DA_Theta_itm', 'DA_Theta', 'DA_Theta_otm','BLS_Theta_itm', 'BLS_Theta', 'BLS_Theta_otm'])
deltaDf['DA_Theta_itm']=[bls.greeks.analytical.theta('c', S0, K-eps, s, r, otm_impVol) for s in linTimeToMaturity]
deltaDf['DA_Theta']=[bls.greeks.analytical.theta('c', S0, K, s, r, otm_impVol) for s in linTimeToMaturity]
deltaDf['DA_Theta_otm']=[bls.greeks.analytical.theta('c', S0, K+eps, s, r,  otm_impVol) for s in linTimeToMaturity]
deltaDf['BLS_Theta_itm']=[bls.greeks.analytical.theta('c', S0, K-eps, s, r, sigma) for s in linTimeToMaturity]
deltaDf['BLS_Theta']=[bls.greeks.analytical.theta('c', S0, K, s,r, sigma) for s in linTimeToMaturity]
deltaDf['BLS_Theta_otm']=[bls.greeks.analytical.theta('c', S0, K+eps, s,r, sigma) for s in linTimeToMaturity]

ax.set_color_cycle(da_colorcycle)
ax.plot(linTimeToMaturity, 
            deltaDf[['DA_Theta_itm', 'DA_Theta', 'DA_Theta_otm']],
            linewidth=2)
            
ax.set_color_cycle(bls_colorcycle)
ax.plot(linTimeToMaturity, 
            deltaDf[['BLS_Theta_itm', 'BLS_Theta', 'BLS_Theta_otm']],
            linestyle='--')
ax.set_xlim(linTimeToMaturity[0], linTimeToMaturity[39])
ax.set_xlabel('Time to Maturity', fontsize=12, fontweight='bold')
ax.set_ylabel('Theta', fontsize=12, fontweight='bold')
ax.set_title('Option Thetas vs Time to Maturity', fontsize=14, fontweight='bold')
ax.legend(['CDA ITM','CDA ATM', 'CDA OTM','BLS ITM','BLS ATM', 'BLS OTM'], loc='lower right', frameon=True, framealpha=0.5,  fontsize=12)
ax.grid(True)

plt.tight_layout()
fig.savefig(outputPath, dpi=300)