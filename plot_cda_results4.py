# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 11:42:21 2015

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

expName='garTraders'
plotFolder='results/cda_experiments/%s/' % expName
outputPath='plots/cda_experiments/%s_FinalBalance' % expName

optionNames=['atm', 'otm', 'itm']
sns.set_style("whitegrid")

fig=plt.figure(figsize=(10,4))
gs=mgridspec.GridSpec(1,2)

da_colorcycle=['darkred', 'red', 'salmon']
bls_colorcycle=['navy', 'blue', 'royalblue']

#Cash Distribution
ax=plt.subplot(gs[0])
itm_marketDf=pd.read_excel(plotFolder+'itm_TraderResults.xls')
atm_marketDf=pd.read_excel(plotFolder+'atm_TraderResults.xls')
otm_marketDf=pd.read_excel(plotFolder+'otm_TraderResults.xls')

itm_marketDf=itm_marketDf[71:]
otm_marketDf=otm_marketDf[71:]
atm_marketDf=atm_marketDf[71:]

itm_marketDf=itm_marketDf.join(otm_marketDf, how='left', lsuffix='_itm', rsuffix='_otm')
itm_marketDf=itm_marketDf.join(atm_marketDf, how='left')
ax.hist(itm_marketDf[['trader_cash_itm','trader_cash', 'trader_cash_otm']].values, histtype='bar', normed=1, color=da_colorcycle)
ax.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.e'))
ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.e'))
ax.set_title('GD Traders Cash at Expiry', fontsize=14, fontweight='bold')
ax.set_xlabel('Cash', fontsize=12, fontweight='bold')
ax.legend(['CDA ITM','CDA ATM', 'CDA OTM'], loc='upper right', frameon=True, framealpha=0.5,  fontsize=12)

#Option Distribution
ax=plt.subplot(gs[1])
ax.hist(itm_marketDf[['trader_options_itm','trader_options', 'trader_options_otm']].values, histtype='bar', normed=1, color=da_colorcycle)
#ax.set_xticks(np.arange(-2e5, 2e5+1, 5e4, dtype='int'))
ax.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.e'))
ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.e'))
ax.set_title('GD Traders Options at Expiry', fontsize=14, fontweight='bold')
ax.set_xlabel('Num of Options', fontsize=12, fontweight='bold')
ax.legend(['CDA ITM','CDA ATM', 'CDA OTM'], loc='upper right', frameon=True, framealpha=0.5,  fontsize=12)

fig.savefig(outputPath, dpi=300)