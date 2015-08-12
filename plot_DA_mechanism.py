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


#primary settings
numTraders=100

r=0.0007
sigma=0.0089
arrRate=0.8
jumpMu=-0.004
jumpSigma=0.0083
S0=100
K=100

#option to trade
opt=CallOption(S0=S0,K=K,r=r,sigma=sigma, T=1)

#asset pricing methods
brwnMdl=BrownianPricing(r, sigma)
jumpDiffMdl=JumpDiffPricing(r, sigma, arrRate, jumpMu, jumpSigma)

#option pricing methods
ziPricer=ZIPricing(assetMdl)

#quantity models
rndModel=RandomQuantity((-2000,2000))
linModel=LinearQuantity((-1000,1200,1000,200))

#traders
traders=DATrader(QuantityModel=rndModel, AssetPricingModel=brwnMdl)


#underlying market
assetPrices=brwnMdl.generate(S0, 1, opt.daysToMaturity(), True).T
interestRates=pd.Series(np.ones(opt.daysToMaturity())*r, name='InterestRate')

#mechanisms
daSim=DirectDASimulator("fixed_brownian_mon_rnd", assetPrices, interestRates, traders, opt, numTraders)
plotDf=daSim.simulate()


plotDf.plot(y=['DAPrice','BLSPrice'])
