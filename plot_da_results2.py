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

expName='mixedAllTraders1'
plotFolder='results/da_experiments/%s/' % expName
outputPath='plots/da_experiments/%s_Greeks' % expName

optionNames=['atm', 'otm', 'itm']
sns.set_style("whitegrid")

fig=plt.figure(figsize=(10,15))
gs=mgridspec.GridSpec(4,2)

da_colorcycle=['darkred', 'red', 'salmon']
bls_colorcycle=['navy', 'blue', 'royalblue']

#Efficiency Errors
ax=plt.subplot(gs[0])
itm_marketDf=pd.read_excel(plotFolder+'itm_Market.xls')
atm_marketDf=pd.read_excel(plotFolder+'atm_Market.xls')
otm_marketDf=pd.read_excel(plotFolder+'otm_Market.xls')

itm_marketDf=itm_marketDf.join(otm_marketDf, how='left', lsuffix='_itm', rsuffix='_otm')
itm_marketDf=itm_marketDf.join(atm_marketDf, how='left')
ax.hist(itm_marketDf[['EffErr_itm','EffErr', 'EffErr_otm']].values, histtype='bar', normed=1, color=da_colorcycle)
ax.set_title('Relative Error in Allocative Efficiency', fontsize=14, fontweight='bold')
ax.set_xlabel('Relative Error', fontsize=12, fontweight='bold')
ax.legend(['DA ITM',' DA ATM', 'DA OTM'], loc='upper right', frameon=True, framealpha=0.5,  fontsize=12)

#Budget Balance
ax=plt.subplot(gs[1])
ax.hist(itm_marketDf[['BB_itm','BB', 'BB_otm']].values,bins=np.arange(-2e5, 2e5+1, 5e4, dtype='int'), histtype='bar', normed=1, color=da_colorcycle)
#ax.set_xticks(np.arange(-2e5, 2e5+1, 5e4, dtype='int'))
ax.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.e'))
ax.set_title('Budget Balance', fontsize=14, fontweight='bold')
ax.set_xlabel('Profit/Loss', fontsize=12, fontweight='bold')
ax.legend(['DA ITM',' DA ATM', 'DA OTM'], loc='upper right', frameon=True, framealpha=0.5,  fontsize=12)

#DELTA
ax=plt.subplot(gs[2])
itm_deltaDf=pd.read_excel(plotFolder+'itm_Delta.xls')
atm_deltaDf=pd.read_excel(plotFolder+'atm_Delta.xls')
otm_deltaDf=pd.read_excel(plotFolder+'otm_Delta.xls')

itm_deltaDf=itm_deltaDf.join(otm_deltaDf, how='left', lsuffix='_itm', rsuffix='_otm')
itm_deltaDf=itm_deltaDf.join(atm_deltaDf, how='left')

ax.set_color_cycle(da_colorcycle)
ax.plot(atm_deltaDf['AssetPrice'], 
            itm_deltaDf[['DA_Delta_itm', 'DA_Delta', 'DA_Delta_otm']],
            linewidth=2)
            
ax.set_color_cycle(bls_colorcycle)
ax.plot(atm_deltaDf['AssetPrice'], 
            itm_deltaDf[['BLS_Delta_itm', 'BLS_Delta', 'BLS_Delta_otm']],
            linestyle='--')
ax.set_xlim(atm_deltaDf['AssetPrice'][0], atm_deltaDf['AssetPrice'][39])
ax.set_xlabel('Asset Prices', fontsize=12, fontweight='bold')
ax.set_ylabel('Delta', fontsize=12, fontweight='bold')
ax.set_title('Option Deltas vs Asset Prices', fontsize=14, fontweight='bold')
ax.legend(['DA ITM',' DA ATM', 'DA OTM','BLS ITM','BLS ATM', 'BLS OTM'], loc='lower right', frameon=True, framealpha=0.5,  fontsize=12)
ax.grid(True)

#DELTA WITH TIME
ax=plt.subplot(gs[3])
itm_deltaDf=pd.read_excel(plotFolder+'itm_DeltaWithTime.xls')
atm_deltaDf=pd.read_excel(plotFolder+'atm_DeltaWithTime.xls')
otm_deltaDf=pd.read_excel(plotFolder+'otm_DeltaWithTime.xls')

itm_deltaDf=itm_deltaDf.join(otm_deltaDf, how='left', lsuffix='_itm', rsuffix='_otm')
itm_deltaDf=itm_deltaDf.join(atm_deltaDf, how='left')

ax.set_color_cycle(da_colorcycle)
ax.plot(atm_deltaDf['TimeToMaturity'], 
            itm_deltaDf[['DA_Delta_itm', 'DA_Delta', 'DA_Delta_otm']],
            linewidth=2)
            
ax.set_color_cycle(bls_colorcycle)
ax.plot(atm_deltaDf['TimeToMaturity'], 
            itm_deltaDf[['BLS_Delta_itm', 'BLS_Delta', 'BLS_Delta_otm']],
            linestyle='--')
ax.set_xlim(atm_deltaDf['TimeToMaturity'][0], atm_deltaDf['TimeToMaturity'][39])
ax.set_xlabel('Time to Maturity', fontsize=12, fontweight='bold')
ax.set_ylabel('Delta', fontsize=12, fontweight='bold')
ax.set_title('Option Deltas vs Time to Maturity', fontsize=14, fontweight='bold')
ax.legend(['DA ITM',' DA ATM', 'DA OTM','BLS ITM','BLS ATM', 'BLS OTM'], loc='lower right', frameon=True, framealpha=0.5,  fontsize=12)
ax.grid(True)

#GAMMA
ax=plt.subplot(gs[4])
itm_deltaDf=pd.read_excel(plotFolder+'itm_Gamma.xls')
atm_deltaDf=pd.read_excel(plotFolder+'atm_Gamma.xls')
otm_deltaDf=pd.read_excel(plotFolder+'otm_Gamma.xls')

itm_deltaDf=itm_deltaDf.join(otm_deltaDf, how='left', lsuffix='_itm', rsuffix='_otm')
itm_deltaDf=itm_deltaDf.join(atm_deltaDf, how='left')

ax.set_color_cycle(da_colorcycle)
ax.plot(atm_deltaDf['AssetPrice'], 
            itm_deltaDf[['DA_Gamma_itm', 'DA_Gamma', 'DA_Gamma_otm']],
            linewidth=2)
            
ax.set_color_cycle(bls_colorcycle)
ax.plot(atm_deltaDf['AssetPrice'], 
            itm_deltaDf[['BLS_Gamma_itm', 'BLS_Gamma', 'BLS_Gamma_otm']],
            linestyle='--')
ax.set_xlim(atm_deltaDf['AssetPrice'][0], atm_deltaDf['AssetPrice'][39])
ax.set_xlabel('Asset Prices', fontsize=12, fontweight='bold')
ax.set_ylabel('Gamma', fontsize=12, fontweight='bold')
ax.set_title('Option Gammas vs Asset Prices', fontsize=14, fontweight='bold')
ax.legend(['DA ITM',' DA ATM', 'DA OTM','BLS ITM','BLS ATM', 'BLS OTM'], loc='lower right', frameon=True, framealpha=0.5,  fontsize=12)
ax.grid(True)

#GAMMA WITH TIME
ax=plt.subplot(gs[5])
itm_deltaDf=pd.read_excel(plotFolder+'itm_GammaWithTime.xls')
atm_deltaDf=pd.read_excel(plotFolder+'atm_GammaWithTime.xls')
otm_deltaDf=pd.read_excel(plotFolder+'otm_GammaWithTime.xls')

itm_deltaDf=itm_deltaDf.join(otm_deltaDf, how='left', lsuffix='_itm', rsuffix='_otm')
itm_deltaDf=itm_deltaDf.join(atm_deltaDf, how='left')

ax.set_color_cycle(da_colorcycle)
ax.plot(atm_deltaDf['TimeToMaturity'], 
            itm_deltaDf[['DA_Gamma_itm', 'DA_Gamma', 'DA_Gamma_otm']],
            linewidth=2)
            
ax.set_color_cycle(bls_colorcycle)
ax.plot(atm_deltaDf['TimeToMaturity'], 
            itm_deltaDf[['BLS_Gamma_itm', 'BLS_Gamma', 'BLS_Gamma_otm']],
            linestyle='--')
ax.set_xlim(atm_deltaDf['TimeToMaturity'][0], atm_deltaDf['TimeToMaturity'][39])
ax.set_xlabel('Time to Maturity', fontsize=12, fontweight='bold')
ax.set_ylabel('Gamma', fontsize=12, fontweight='bold')
ax.set_title('Option Gammas vs Time to Maturity', fontsize=14, fontweight='bold')
ax.legend(['DA ITM',' DA ATM', 'DA OTM','BLS ITM','BLS ATM', 'BLS OTM'], loc='upper right', frameon=True, framealpha=0.5,  fontsize=12)
ax.grid(True)

#THETA
ax=plt.subplot(gs[6])
itm_deltaDf=pd.read_excel(plotFolder+'itm_Theta.xls')
atm_deltaDf=pd.read_excel(plotFolder+'atm_Theta.xls')
otm_deltaDf=pd.read_excel(plotFolder+'otm_Theta.xls')

itm_deltaDf=itm_deltaDf.join(otm_deltaDf, how='left', lsuffix='_itm', rsuffix='_otm')
itm_deltaDf=itm_deltaDf.join(atm_deltaDf, how='left')

ax.set_color_cycle(da_colorcycle)
ax.plot(atm_deltaDf['AssetPrice'], 
            itm_deltaDf[['DA_Theta_itm', 'DA_Theta', 'DA_Theta_otm']],
            linewidth=2)
            
ax.set_color_cycle(bls_colorcycle)
ax.plot(atm_deltaDf['AssetPrice'], 
            itm_deltaDf[['BLS_Theta_itm', 'BLS_Theta', 'BLS_Theta_otm']],
            linestyle='--')
ax.set_xlim(atm_deltaDf['AssetPrice'][0], atm_deltaDf['AssetPrice'][39])
ax.set_xlabel('Asset Prices', fontsize=12, fontweight='bold')
ax.set_ylabel('Theta', fontsize=12, fontweight='bold')
ax.set_title('Option Thetas vs Asset Prices', fontsize=14, fontweight='bold')
ax.legend(['DA ITM',' DA ATM', 'DA OTM','BLS ITM','BLS ATM', 'BLS OTM'], loc='lower right', frameon=True, framealpha=0.5,  fontsize=12)
ax.grid(True)

#THETA WITH TIME
ax=plt.subplot(gs[7])
itm_deltaDf=pd.read_excel(plotFolder+'itm_ThetaWithTime.xls')
atm_deltaDf=pd.read_excel(plotFolder+'atm_ThetaWithTime.xls')
otm_deltaDf=pd.read_excel(plotFolder+'otm_ThetaWithTime.xls')

itm_deltaDf=itm_deltaDf.join(otm_deltaDf, how='left', lsuffix='_itm', rsuffix='_otm')
itm_deltaDf=itm_deltaDf.join(atm_deltaDf, how='left')

ax.set_color_cycle(da_colorcycle)
ax.plot(atm_deltaDf['TimeToMaturity'], 
            itm_deltaDf[['DA_Theta_itm', 'DA_Theta', 'DA_Theta_otm']],
            linewidth=2)
            
ax.set_color_cycle(bls_colorcycle)
ax.plot(atm_deltaDf['TimeToMaturity'], 
            itm_deltaDf[['BLS_Theta_itm', 'BLS_Theta', 'BLS_Theta_otm']],
            linestyle='--')
ax.set_xlim(atm_deltaDf['TimeToMaturity'][0], atm_deltaDf['TimeToMaturity'][39])
ax.set_xlabel('Time to Maturity', fontsize=12, fontweight='bold')
ax.set_ylabel('Theta', fontsize=12, fontweight='bold')
ax.set_title('Option Thetas vs Time to Maturity', fontsize=14, fontweight='bold')
ax.legend(['DA ITM',' DA ATM', 'DA OTM','BLS ITM','BLS ATM', 'BLS OTM'], loc='lower right', frameon=True, framealpha=0.5,  fontsize=12)
ax.grid(True)

plt.tight_layout()
fig.savefig(outputPath, dpi=300)