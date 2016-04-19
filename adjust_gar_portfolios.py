# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 13:13:44 2015

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
from phd_utils.tradingAlgos.DATrader import *
import scipy.optimize as optim
from scipy.misc import derivative
import scipy.stats as stats
import matplotlib.pyplot as plt
from orderbook import OrderBook
from orderbook.ordertree import OrderTree

optionType="atm"
optionPayoff=36.09921998

tradersDf=pd.read_pickle('./results/cda_experiments/garTraders2/%s_TraderOrders.xls' % optionType)
traderResults=[[i, (tradersDf.ix[363][i]['cash']-tradersDf.ix[0][i]['cash'])+float(tradersDf.ix[363][i]['options']-tradersDf.ix[0][i]['options'])*optionPayoff, tradersDf.ix[363][i]['options']-tradersDf.ix[0][i]['options']] for i in range(1,99)]
traderResultsDf=pd.DataFrame(traderResults, columns=['trader_id', 'trader_cash', 'trader_options'])
traderResultsDf.to_excel("%s/%s_%s.xls" % ("results/cda_experiments/garTraders2", optionType , "TraderResults"))