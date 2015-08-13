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
S0=3563.57
K=3563.57

#option to trade
opt=CallOption(S0=S0,K=K,r=r,sigma=sigma, T=1)

matTime=np.linspace(opt.T, 0, 20)
linAssetPrices=pd.Series(np.linspace(3465,3665,20), name='AssetPrices')

#asset pricing methods
brwnMdl=BrownianPricing(r, sigma)
jumpDiffMdl=JumpDiffPricing(r, sigma, arrRate, jumpMu, jumpSigma)

#option pricing methods
ziOptPricer=ZIPricing(brwnMdl)
expOptPricer=ExpPricing(brwnMdl, 0.1)

#quantity models
rndModel=RandomQuantity((-2000,2000))
linModel=LinearQuantity((-1000,1200,1000,200))

#traders
expTrader=DATrader(QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=expOptPricer)
monBrwnTrader=DATrader(QuantityModel=rndModel, AssetPricingModel=brwnMdl)
monJumpDiffTrader=DATrader(QuantityModel=rndModel, AssetPricingModel=jumpDiffMdl)

#trader collection
mixedTraders=DATraderCollection([expTrader, monBrwnTrader, monJumpDiffTrader], [0.3,0.3,0.4])

#underlying market
assetPrices=brwnMdl.generate(S0, 1, opt.daysToMaturity(), True).T[0]
interestRates=pd.Series(np.ones(opt.daysToMaturity())*r, name='InterestRate')

#mechanisms
daSim=DirectDASimulator("fixed_brownian_mon_rnd", assetPrices, interestRates, monJumpDiffTrader, opt, numTraders)
#daMixedSim=DirectDASimulator("fixed_mixed1",  assetPrices, interestRates, mixedTraders, opt, numTraders)


#plotDf=daMixedSim.simulate()
#plotDf.plot(y=['BLSPrice', 'DAPrice'])

#plotDf=daSim.simulateDeltaWithTime(matTime)
#plotDf.plot(x='TimeToMaturity', y=['DA_Delta', 'BLS_Delta'])

#plotDf=daSim.simulateBSGamma(linAssetPrices)
#plotDf.plot(x='AssetPrice', y=['DA_Gamma', 'BLS_Gamma'])

#plotDf=daSim.simulateGammaWithTime(matTime)
#plotDf.plot(x='TimeToMaturity', y=['DA_Gamma', 'BLS_Gamma'])

#plotDf=daSim.simulateBSDelta(linAssetPrices)
#plotDf.plot(x='AssetPrice', y=['DA_Delta', 'BLS_Delta'])

#plotDf=daSim.simulateBSDeltaWithTime(matTime)
#plotDf.plot(x='TimeToMaturity', y=['DA_Delta', 'BLS_Delta'])

#plotDf=daSim.simulateBSTheta(linAssetPrices)
#plotDf.plot(x='AssetPrice', y=['DA_Theta', 'BLS_Theta'])

#plotDf=daSim.simulateBSThetaWithTime(matTime)
#plotDf.plot(x='TimeToMaturity', y=['DA_Theta', 'BLS_Theta'])

plotDf=daSim.simulateVolCurve(linAssetPrices)
plotDf.plot(x='Strikes', y='ImpVol')

