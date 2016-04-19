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

margin = 1
ind = np.arange(0,18,3)+margin*np.arange(0,6)  # the x locations for the groups
ind2 = ind+1
ind3=ind+2


fig=plt.figure(figsize=(10,4))
gs=mgridspec.GridSpec(1,2)

da_colorcycle=['darkred', 'red', 'salmon']
bls_colorcycle=['navy', 'blue', 'royalblue']

#Cash Distribution
ax=plt.subplot(gs[0])
itm_marketDf=pd.read_excel(plotFolder+'itm_TraderResults.xls')
atm_marketDf=pd.read_excel(plotFolder+'atm_TraderResults.xls')
otm_marketDf=pd.read_excel(plotFolder+'otm_TraderResults.xls')

itm_marketDf=itm_marketDf[0:6]
otm_marketDf=otm_marketDf[0:6]
atm_marketDf=atm_marketDf[0:6]

itm_marketDf=itm_marketDf.join(otm_marketDf, how='left', lsuffix='_itm', rsuffix='_otm')
itm_marketDf=itm_marketDf.join(atm_marketDf, how='left')
ax.bar(ind, itm_marketDf['trader_cash_itm'].values, color='darkred')
ax.bar(ind2, itm_marketDf['trader_cash'].values, color='red')
ax.bar(ind3, itm_marketDf['trader_cash_otm'].values, color='salmon')

ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.e'))
ax.set_title('GAR Dealers Cash at Expiry', fontsize=14, fontweight='bold')
ax.set_xlabel('Dealers', fontsize=12, fontweight='bold')
ax.set_xticks(ind2+0.8)
ax.set_xticklabels( ('GAR1', 'GAR2', 'GAR3', 'GAR4', 'GAR5', 'GAR6') )
ax.legend(['CDA ITM','CDA ATM', 'CDA OTM'], loc='lower left', frameon=True, framealpha=0.5,  fontsize=12)

#Option Distribution
ax=plt.subplot(gs[1])
ax.bar(ind, itm_marketDf['trader_options_itm'].values, color='darkred')
ax.bar(ind2, itm_marketDf['trader_options'].values, color='red')
ax.bar(ind3, itm_marketDf['trader_options_otm'].values, color='salmon')

ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.e'))
ax.set_title('GAR Dealers Options at Expiry', fontsize=14, fontweight='bold')
ax.set_xlabel('Dealers', fontsize=12, fontweight='bold')
ax.set_xticks(ind2+0.8)
ax.set_xticklabels( ('GAR1', 'GAR2', 'GAR3', 'GAR4', 'GAR5', 'GAR6') )
#ax.legend(['CDA ITM','CDA ATM', 'CDA OTM'], loc='upper left', frameon=True, framealpha=0.5,  fontsize=12)

plt.tight_layout()
fig.savefig(outputPath, dpi=300)