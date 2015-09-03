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

assetPrices=pd.read_excel('data/brwn_assetPrices.xls')[0]

plt.plot(assetPrices)
plt.xlabel('Days', fontsize=12)
plt.ylabel('Price', fontsize=12)
plt.xlim([0, 365])
plt.title('Simulated NASDAQ-100 Indices', fontsize=14, fontweight='bold')