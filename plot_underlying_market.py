# -*- coding: utf-8 -*-
"""
Created on Tue Sep 01 07:48:57 2015

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

#assetPrices=pd.read_excel('data/brwn_assetPrices.xls')[0]
#
#plt.plot(assetPrices)
#plt.xlabel('Days', fontsize=12)
#plt.ylabel('Price', fontsize=12)
#plt.xlim([0, 365])
#plt.title('Simulated NASDAQ-100 Indices', fontsize=14, fontweight='bold')
gs=mgridspec.GridSpec(2,1, height_ratios=[3,1])
sns.set_style("whitegrid")
marketDf=pd.read_excel('results/da_experiments/exp_rnd_degen/exp_rnd_mc20_Market.xls')
ax1=plt.subplot(gs[0])
#plt.gca().set_color_cycle(['blue', 'red'])

daPrices, =ax1.plot(marketDf.index, marketDf['DAPrice'], color='red', label='DA Price')
blsPrices, =ax1.plot(marketDf.index, marketDf['BLSPrice'], color='blue', label='Black-Scholes Price')
ax1.fill_between(marketDf.index,  marketDf['accepted_ask_min'], marketDf['accepted_bid_max'], facecolor='yellow', alpha=0.4)
#    ax1.fill_between(marketDf.index,  marketDf['rejected_ask_min'], marketDf['rejected_ask_max'], facecolor='yellow', alpha=0.4)
#    ax1.fill_between(marketDf.index,  marketDf['rejected_bid_min'], marketDf['rejected_bid_max'], facecolor='yellow', alpha=0.4)

acceptedOrders=mpatches.Patch(color='yellow', label='Accepted Orders')
#    rejectedOrders=mpatches.Patch(color='yellow', label='Rejected Orders')
volumePatch=mpatches.Patch(color='gray', label='Traded Volume')
effErrPatch=mpatches.Patch(color='b', label='Rejected Efficient Trades')

plt.setp(ax1.get_xticklabels(), visible=False)
ax1.grid(True)

ax1.set_xlim([0, marketDf.index[-1]])
ax1.set_title('ATM Option Prices until Expiration Date', fontsize=14, fontweight='bold')
ax1.set_ylabel('Option Prices', fontsize=14, fontweight='bold')

ax1.legend(loc='upper right', frameon=True, framealpha=0.7,  fontsize=12, handles=[blsPrices, daPrices, acceptedOrders])


ax2=plt.subplot(gs[1])
vols=np.row_stack((marketDf['Volume'], marketDf['Volume']*(1+marketDf['EffErr'])))
ax2.fill_between(marketDf.index, 0, vols[0,:], facecolor='gray', alpha=.6)
ax2.fill_between(marketDf.index, vols[0,:], vols[1,:], facecolor='b')

ax2.set_xlim([0, marketDf.index[-1]])

ax2.set_ylabel('Volume', fontsize=14, fontweight='bold')
plt.setp(ax2.get_xticklabels(), visible=False)

ax2.set_xlabel('Time', fontsize=14, fontweight='bold')
plt.setp(ax2.get_xticklabels(), visible=True)
plt.tight_layout()
plt.savefig('exp_rnd_mc20_Market.png', dpi=300)