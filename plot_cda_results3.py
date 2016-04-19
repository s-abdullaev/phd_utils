# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 17:52:01 2015

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

trader_id=6
trader_name='GAR(cash=1M,options=1M)'
chart_title='%s Trader Performance' % trader_name
expName='garTraders'
plotFolder='results/cda_experiments/%s/' % expName
outputPath='plots/cda_experiments/%s_TraderPerformance_%s' % (expName, trader_id)

df=pd.read_pickle(plotFolder+'atm_TraderOrders.xls')
marketDf=pd.read_excel(plotFolder+'atm_Market.xls')
tr=df[:][trader_id]

sns.set_style("whitegrid")

fig=plt.figure(figsize=(7,7))
gs=mgridspec.GridSpec(3,1, height_ratios=[3,1,1])

da_colorcycle=['darkred', 'red', 'salmon']
bls_colorcycle=['navy', 'blue', 'royalblue']

#bid ask spread
ax=plt.subplot(gs[0])
blsPrices, =ax.plot(marketDf.index, marketDf['BLSPrice'], color='blue', label='Black-Scholes Price')
daPrices, =ax.plot(marketDf.index, tr['pHat'], color='red', label='Trader Price')
ax.fill_between(marketDf.index,  tr['bid'], tr['ask'], facecolor='gray', alpha=0.6)
    
acceptedOrders=mpatches.Patch(color='gray', label='Bid-Ask')
    
plt.setp(ax.get_xticklabels(), visible=False)
ax.grid(True)
ax.set_xlim([0, marketDf.index[-1]])
ax.set_title(chart_title, fontsize=14, fontweight='bold')
ax.set_ylabel('Option Prices', fontsize=14, fontweight='bold')
ax.legend(loc='upper right', frameon=True, framealpha=0.7,  fontsize=12, handles=[blsPrices, daPrices, acceptedOrders])
    
ax=plt.subplot(gs[1])
ax.plot(marketDf.index, tr['cash'], color='blue')
ax.set_xlim([0, marketDf.index[-1]])
ax.set_ylabel('Cash', fontsize=14, fontweight='bold')
ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.e'))
plt.setp(ax.get_xticklabels(), visible=False)

ax=plt.subplot(gs[2])
ax.plot(marketDf.index, tr['options'], color='blue')
ax.set_ylabel('Options', fontsize=14, fontweight='bold')
ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.e'))
ax.set_xlim([0, marketDf.index[-1]])

plt.tight_layout()
fig.savefig(outputPath, dpi=300)