# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 02:19:31 2015

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
import scipy.stats as stats
import matplotlib.pyplot as plt

np.random.seed=400

r=0.01
sigma=0.5
arrRate=4
jumpMu=0.05
jumpSigma=0.2

assetMdl=JumpDiffPricing(r, sigma, arrRate, jumpMu, jumpSigma)
opt=CallOption(S0=100,K=100,r=r,sigma=sigma, T=1)


ziPricer=ZIPricing(assetMdl)


rndModel=RandomQuantity((-2000,2000))
linModel=LinearQuantity((-200,1000,500,1000))

trader=DATrader()
mechanism=DirectDA()

steps=np.linspace(opt.T, 0, opt.daysToMaturity())
assetPrices=assetMdl.generate(100, 1, opt.daysToMaturity(), True).T

plotDf=pd.DataFrame(np.zeros([opt.daysToMaturity(), 4]), columns=['DAPrice', 'BLSPrice', 'Volume', 'AssetPrice'])

plotDf['AssetPrice']=assetPrices.values
for i, t, p in zip(range(opt.daysToMaturity()), steps, assetPrices[0].values):
    opt.T=t
    opt.S0=p    
        
    orders=trader.getOrders(opt, 100, QuantityModel=rndModel, AssetPricingModel=BrownianPricing(r, sigma))
    orders=mechanism.clearOrders(orders)
    plotDf.ix[i]['DAPrice']=mechanism.getPrice(orders)
    plotDf.ix[i]['Volume']=mechanism.getVolume(orders)
    plotDf.ix[i]['BLSPrice']=opt.blsPrice()
    print i

plotDf.plot(y=['DAPrice','BLSPrice'])
