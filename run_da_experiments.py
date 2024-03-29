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
from phd_utils.mechanisms.online_models import *
from phd_utils.mechanisms.experiment import *
from phd_utils.tradingAlgos.DATrader import *
import scipy.optimize as optim
import scipy.stats as stats
import matplotlib.pyplot as plt
import sys


#primary settings
numTraders=100

r=0.0007
sigma=0.0089
arrRate=0.8
jumpMu=-0.004
jumpSigma=0.0083
S0=3563.57
K=3563.57
eps=40
T=1

sigma_eps=0.001

r_mu=0.2555
r_sigma=0.09
r_theta=0.46
r_arrRate=4
r_muLambda=0.1
r_sigmaLambda=0.2

risk_aversion=0.03
lmsr_liquidity=100

ntrials=100


qnty_random=(-2000,2000)
qnty_const=(0,1200,0,1200)
equib_quant=2000


#lin assets and maturity                         
linTime=np.linspace(T, 0, 50)
linAssetPrices=pd.Series(np.arange(3465,3665,5.0), name='AssetPrices')

#option to trade
call_atm=CallOption(S0=S0,K=K,r=r,sigma=sigma, T=T)
put_atm=PutOption(S0=S0,K=K,r=r,sigma=sigma, T=T)

call_itm=CallOption(S0=S0,K=K-eps,r=r,sigma=sigma, T=T)
call_otm=CallOption(S0=S0,K=K+eps,r=r,sigma=sigma, T=T)

#option portfolios
port_neutral1=OptionPortfolio(call_atm, put_atm, eps, OPTION_PORTFOLIOS.ix['Butterfly Call Spread'])
port_neutral2=OptionPortfolio(call_atm, put_atm, eps, OPTION_PORTFOLIOS.ix['Iron Butterfly'])
port_neutral3=OptionPortfolio(call_atm, put_atm, eps, OPTION_PORTFOLIOS.ix['Long Call Ladder'])
port_neutral4=OptionPortfolio(call_atm, put_atm, eps, OPTION_PORTFOLIOS.ix['Short Strangle'])
port_neutral5=OptionPortfolio(call_atm, put_atm, eps, OPTION_PORTFOLIOS.ix['Short Straddle'])

port_non_neutral1=OptionPortfolio(call_atm, put_atm, eps, OPTION_PORTFOLIOS.ix['Short Call Ladder'])
port_non_neutral2=OptionPortfolio(call_atm, put_atm, eps, OPTION_PORTFOLIOS.ix['Long Straddle'])
port_non_neutral3=OptionPortfolio(call_atm, put_atm, eps, OPTION_PORTFOLIOS.ix['Long Strangle'])
port_non_neutral4=OptionPortfolio(call_atm, put_atm, eps, OPTION_PORTFOLIOS.ix['Strip'])
port_non_neutral5=OptionPortfolio(call_atm, put_atm, eps, OPTION_PORTFOLIOS.ix['Strap'])

port_bullish1=OptionPortfolio(call_atm, put_atm, eps, OPTION_PORTFOLIOS.ix['Long Call'])
port_bullish2=OptionPortfolio(call_atm, put_atm, eps, OPTION_PORTFOLIOS.ix['Bull Call Spread'])

port_bearish1=OptionPortfolio(call_atm, put_atm, eps, OPTION_PORTFOLIOS.ix['Long Put'])
port_bearish2=OptionPortfolio(call_atm, put_atm, eps, OPTION_PORTFOLIOS.ix['Bear Call Spread'])

#asset pricing models
brwnMdl=BrownianPricing(r, sigma)
jumpDiffMdl=JumpDiffPricing(r, sigma, arrRate, jumpMu, jumpSigma)

#interest rate models
vasicekMdl=VasicekPricing(r_mu, r_sigma, r_theta)
vasicekJumpMdl=VasicekJumpPricing(r_mu, r_sigma, r_theta, r_arrRate, r_muLambda, r_sigmaLambda)

#option pricing methods
ziOptPricer=ZIPricing(brwnMdl)
expOptPricer=ExpPricing(brwnMdl, risk_aversion)
monOptPricer=MonteCarloPricing(brwnMdl, ntrials)
monJdOptPricer=MonteCarloPricing(jumpDiffMdl, ntrials)
bsOptPricer=BSPricing(r, sigma, sigma_eps)

lmsr_neutralPricer1=LMSRPricing(brwnMdl, ntrials, lmsr_liquidity, port_neutral1)
lmsr_neutralPricer2=LMSRPricing(brwnMdl, ntrials, lmsr_liquidity, port_neutral2)
lmsr_neutralPricer3=LMSRPricing(brwnMdl, ntrials, lmsr_liquidity, port_neutral3)
lmsr_neutralPricer4=LMSRPricing(brwnMdl, ntrials, lmsr_liquidity, port_neutral4)
lmsr_neutralPricer5=LMSRPricing(brwnMdl, ntrials, lmsr_liquidity, port_neutral5)

lmsr_nonNeutralPricer1=LMSRPricing(brwnMdl, ntrials, lmsr_liquidity, port_non_neutral1)
lmsr_nonNeutralPricer2=LMSRPricing(brwnMdl, ntrials, lmsr_liquidity, port_non_neutral2)
lmsr_nonNeutralPricer3=LMSRPricing(brwnMdl, ntrials, lmsr_liquidity, port_non_neutral3)
lmsr_nonNeutralPricer4=LMSRPricing(brwnMdl, ntrials, lmsr_liquidity, port_non_neutral4)
lmsr_nonNeutralPricer5=LMSRPricing(brwnMdl, ntrials, lmsr_liquidity, port_non_neutral5)

lmsr_bullPricer1=LMSRPricing(brwnMdl, ntrials, lmsr_liquidity, port_bullish1)
lmsr_bullPricer2=LMSRPricing(brwnMdl, ntrials, lmsr_liquidity, port_bullish2)

lmsr_bearPricer1=LMSRPricing(brwnMdl, ntrials, lmsr_liquidity, port_bearish1)
lmsr_bearPricer2=LMSRPricing(brwnMdl, ntrials, lmsr_liquidity, port_bearish2)

#quantity models
rndModel=RandomQuantity(qnty_random)
rndSingModel=RandomSingularQuantity()
linModel=LinearQuantity(equib_quant)
constModel=LinearQuantity(qnty_const)

#traders
zi_rnd_trader=DATrader(QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=ziOptPricer)

exp_rnd_trader=DATrader(QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=expOptPricer)
mon_rnd_brwn_trader=DATrader(QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer)
mon_rnd_jd_trader=DATrader(QuantityModel=rndModel, AssetPricingModel=jumpDiffMdl, OptionPricingModel=monJdOptPricer)
bs_rnd_trader=DATrader(QuantityModel=rndModel, OptionPricingModel=bsOptPricer)

lmsr_rnd_neutralTrader1=DATrader(QuantityModel=rndModel, OptionPricingModel=lmsr_neutralPricer1)
lmsr_rnd_neutralTrader2=DATrader(QuantityModel=rndModel, OptionPricingModel=lmsr_neutralPricer2)
lmsr_rnd_neutralTrader3=DATrader(QuantityModel=rndModel, OptionPricingModel=lmsr_neutralPricer3)
lmsr_rnd_neutralTrader4=DATrader(QuantityModel=rndModel, OptionPricingModel=lmsr_neutralPricer4)
lmsr_rnd_neutralTrader5=DATrader(QuantityModel=rndModel, OptionPricingModel=lmsr_neutralPricer5)

lmsr_rnd_nonNeutralTrader1=DATrader(QuantityModel=rndModel, OptionPricingModel=lmsr_nonNeutralPricer1)
lmsr_rnd_nonNeutralTrader2=DATrader(QuantityModel=rndModel, OptionPricingModel=lmsr_nonNeutralPricer2)
lmsr_rnd_nonNeutralTrader3=DATrader(QuantityModel=rndModel, OptionPricingModel=lmsr_nonNeutralPricer3)
lmsr_rnd_nonNeutralTrader4=DATrader(QuantityModel=rndModel, OptionPricingModel=lmsr_nonNeutralPricer4)
lmsr_rnd_nonNeutralTrader5=DATrader(QuantityModel=rndModel, OptionPricingModel=lmsr_nonNeutralPricer5)

lmsr_rnd_bullTrader1=DATrader(QuantityModel=rndModel, OptionPricingModel=lmsr_bullPricer1)
lmsr_rnd_bullTrader2=DATrader(QuantityModel=rndModel, OptionPricingModel=lmsr_bullPricer2)

lmsr_rnd_bearTrader1=DATrader(QuantityModel=rndModel, OptionPricingModel=lmsr_bearPricer1)
lmsr_rnd_bearTrader2=DATrader(QuantityModel=rndModel, OptionPricingModel=lmsr_bearPricer2)

lmsr_lin_neutralTrader1=DATrader(QuantityModel=linModel, OptionPricingModel=lmsr_neutralPricer1)
lmsr_lin_neutralTrader2=DATrader(QuantityModel=linModel, OptionPricingModel=lmsr_neutralPricer2)
lmsr_lin_neutralTrader3=DATrader(QuantityModel=linModel, OptionPricingModel=lmsr_neutralPricer3)
lmsr_lin_neutralTrader4=DATrader(QuantityModel=linModel, OptionPricingModel=lmsr_neutralPricer4)
lmsr_lin_neutralTrader5=DATrader(QuantityModel=linModel, OptionPricingModel=lmsr_neutralPricer5)

lmsr_lin_nonNeutralTrader1=DATrader(QuantityModel=linModel, OptionPricingModel=lmsr_nonNeutralPricer1)
lmsr_lin_nonNeutralTrader2=DATrader(QuantityModel=linModel, OptionPricingModel=lmsr_nonNeutralPricer2)
lmsr_lin_nonNeutralTrader3=DATrader(QuantityModel=linModel, OptionPricingModel=lmsr_nonNeutralPricer3)
lmsr_lin_nonNeutralTrader4=DATrader(QuantityModel=linModel, OptionPricingModel=lmsr_nonNeutralPricer4)
lmsr_lin_nonNeutralTrader5=DATrader(QuantityModel=linModel, OptionPricingModel=lmsr_nonNeutralPricer5)

lmsr_lin_bullTrader1=DATrader(QuantityModel=linModel, OptionPricingModel=lmsr_bullPricer1)
lmsr_lin_bullTrader2=DATrader(QuantityModel=linModel, OptionPricingModel=lmsr_bullPricer2)

lmsr_lin_bearTrader1=DATrader(QuantityModel=linModel, OptionPricingModel=lmsr_bearPricer1)
lmsr_lin_bearTrader2=DATrader(QuantityModel=linModel, OptionPricingModel=lmsr_bearPricer2)

exp_lin_trader=DATrader(QuantityModel=linModel, AssetPricingModel=brwnMdl, OptionPricingModel=expOptPricer)
mon_lin_brwn_trader=DATrader(QuantityModel=linModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer)
mon_lin_jd_trader=DATrader(QuantityModel=linModel, AssetPricingModel=jumpDiffMdl, OptionPricingModel=monJdOptPricer)
bs_lin_trader=DATrader(QuantityModel=linModel, OptionPricingModel=bsOptPricer)

exp_const_trader=DATrader(QuantityModel=constModel, AssetPricingModel=brwnMdl, OptionPricingModel=expOptPricer)
mon_const_brwn_trader=DATrader(QuantityModel=constModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer)
mon_const_jd_trader=DATrader(QuantityModel=constModel, AssetPricingModel=jumpDiffMdl, OptionPricingModel=monJdOptPricer)
bs_const_trader=DATrader(QuantityModel=constModel, OptionPricingModel=bsOptPricer)


#trader collection
mixedRiskNeutralTraders1=DATraderCollection([mon_rnd_brwn_trader, mon_rnd_jd_trader, bs_rnd_trader], [0.3,0.3,0.4])
mixedRiskNeutralTraders2=DATraderCollection([mon_rnd_brwn_trader, mon_rnd_jd_trader, bs_rnd_trader], [0.2,0.6,0.2])

mixedRiskNeutralLinTraders1=DATraderCollection([mon_rnd_brwn_trader, mon_lin_jd_trader, bs_rnd_trader], [0.3,0.3,0.4])
mixedRiskNeutralLinTraders2=DATraderCollection([mon_rnd_brwn_trader, mon_lin_jd_trader, bs_rnd_trader], [0.2,0.6,0.2])

mixedTraders1=DATraderCollection([exp_rnd_trader, zi_rnd_trader], [0.8,0.2])
mixedTraders2=DATraderCollection([exp_rnd_trader, zi_rnd_trader, bs_rnd_trader], [0.4,0.4,0.2])

mixedAllTraders=DATraderCollection([mon_rnd_brwn_trader,
                                    mon_rnd_jd_trader,
                                    mon_lin_brwn_trader,
                                    mon_lin_jd_trader,
                                    exp_rnd_trader,
                                    bs_rnd_trader,
                                    lmsr_rnd_neutralTrader1,
                                    lmsr_rnd_nonNeutralTrader1,
                                    lmsr_rnd_bullTrader2,
                                    lmsr_rnd_bearTrader2], [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1])

mixedLmsrTraders1=DATraderCollection([lmsr_rnd_neutralTrader1, lmsr_rnd_neutralTrader2, lmsr_rnd_nonNeutralTrader1, lmsr_rnd_nonNeutralTrader2], [0.25,0.25,0.25,0.25])
mixedLmsrTraders2=DATraderCollection([lmsr_rnd_neutralTrader1, lmsr_rnd_bullTrader2, lmsr_rnd_bearTrader2, lmsr_rnd_nonNeutralTrader1], [0.25,0.25,0.25,0.25])
mixedLmsrTraders3=DATraderCollection([lmsr_rnd_neutralTrader3, lmsr_rnd_bullTrader2, lmsr_rnd_bearTrader2, lmsr_rnd_nonNeutralTrader3], [0.1,0.7,0.1,0.1])
mixedLmsrTraders4=DATraderCollection([lmsr_rnd_neutralTrader4, lmsr_rnd_bullTrader2, lmsr_rnd_bearTrader2, lmsr_rnd_nonNeutralTrader4], [0.1,0.1,0.7,0.1])

mixedLmsrLinTraders1=DATraderCollection([lmsr_lin_neutralTrader1, lmsr_lin_neutralTrader2, lmsr_lin_nonNeutralTrader1, lmsr_lin_nonNeutralTrader2], [0.25,0.25,0.25,0.25])
mixedLmsrLinTraders2=DATraderCollection([lmsr_lin_neutralTrader1, lmsr_lin_bullTrader2, lmsr_lin_bearTrader2, lmsr_lin_nonNeutralTrader1], [0.25,0.25,0.25,0.25])
mixedLmsrLinTraders3=DATraderCollection([lmsr_lin_neutralTrader3, lmsr_lin_bullTrader2, lmsr_lin_bearTrader2, lmsr_lin_nonNeutralTrader3], [0.1,0.7,0.1,0.1])
mixedLmsrLinTraders4=DATraderCollection([lmsr_lin_neutralTrader4, lmsr_lin_bullTrader2, lmsr_lin_bearTrader2, lmsr_lin_nonNeutralTrader4], [0.1,0.1,0.7,0.1])

#underlying market
assetPrices=pd.read_excel('data/brwn_assetPrices.xls')[0]
interestRates=pd.Series(np.ones(call_atm.daysToMaturity())*r, name='InterestRate')
vasicekRates=pd.read_excel('data/vasicek_indices.xls')[0]
vasicekJumpRates=pd.read_excel('data/vasicekJump_indices.xls')[0]


#EXPERIMENTS
exper=[]

#EXP MIXED
#exper.append(DAExperiment("results/da_experiments/mixedTraders1", 
#                        assetPrices, 
#                        interestRates, 
#                        mixedTraders1,
#                        [call_atm, call_otm, call_itm], 
#                        numTraders, 
#                        linAssetPrices,
#                        linTime))
#
#exper.append(DAExperiment("results/da_experiments/mixedTraders2", 
#                        assetPrices, 
#                        interestRates, 
#                        mixedTraders2,
#                        [call_atm, call_otm, call_itm], 
#                        numTraders, 
#                        linAssetPrices,
#                        linTime))
#
#exper.append(DAExperiment("results/da_experiments/mixedTraders3", 
#                        assetPrices, 
#                        interestRates, 
#                        mixedTraders3,
#                        [call_atm, call_otm, call_itm], 
#                        numTraders, 
#                        linAssetPrices,
#                        linTime))
#RISK NEUTRAL TRADERS
#exper.append(DAExperiment("results/da_experiments/mon_rnd_brwn", 
#                        assetPrices, 
#                        interestRates, 
#                        mon_rnd_brwn_trader,
#                        [call_atm, call_otm, call_itm], 
#                        numTraders, 
#                        linAssetPrices,
#                        linTime))
#
#exper.append(DAExperiment("results/da_experiments/mon_rnd_jd", 
#                        assetPrices, 
#                        interestRates, 
#                        mon_rnd_jd_trader,
#                        [call_atm, call_otm, call_itm], 
#                        numTraders, 
#                        linAssetPrices,
#                        linTime))
#
#exper.append(DAExperiment("results/da_experiments/vol_rnd", 
#                        assetPrices, 
#                        interestRates, 
#                        bs_rnd_trader,
#                        [call_atm, call_otm, call_itm], 
#                        numTraders, 
#                        linAssetPrices,
#                        linTime))
#
#exper.append(DAExperiment("results/da_experiments/vol_rnd_vasicek", 
#                        assetPrices, 
#                        vasicekRates, 
#                        bs_rnd_trader,
#                        [call_atm, call_otm, call_itm], 
#                        numTraders, 
#                        linAssetPrices,
#                        linTime))
#
#exper.append(DAExperiment("results/da_experiments/vol_rnd_vasicekJump", 
#                        assetPrices, 
#                        vasicekJumpRates, 
#                        bs_rnd_trader,
#                        [call_atm, call_otm, call_itm], 
#                        numTraders, 
#                        linAssetPrices,
#                        linTime))

#exper.append(DAExperiment("results/da_experiments/mon_lin_brwn", 
#                        assetPrices, 
#                        interestRates, 
#                        mon_lin_brwn_trader,
#                        [call_atm, call_otm, call_itm], 
#                        numTraders, 
#                        linAssetPrices,
#                        linTime))
#
#exper.append(DAExperiment("results/da_experiments/mon_lin_jd", 
#                        assetPrices, 
#                        interestRates, 
#                        mon_lin_jd_trader,
#                        [call_atm, call_otm, call_itm], 
#                        numTraders, 
#                        linAssetPrices,
#                        linTime))

#exper.append(DAExperiment("results/da_experiments/vol_lin", 
#                        assetPrices, 
#                        interestRates, 
#                        bs_lin_trader,
#                        [call_atm, call_otm, call_itm], 
#                        numTraders, 
#                        linAssetPrices,
#                        linTime))

#RISK AVERSE TRADERS
#exper.append(DAExperiment("results/da_experiments/exp_rnd", 
#                        assetPrices, 
#                        interestRates, 
#                        exp_rnd_trader,
#                        [call_atm, call_otm, call_itm], 
#                        numTraders, 
#                        linAssetPrices,
#                        linTime))
#
#exper.append(DAExperiment("results/da_experiments/exp_lin", 
#                        assetPrices, 
#                        interestRates, 
#                        exp_lin_trader,
#                        [call_atm, call_otm, call_itm], 
#                        numTraders, 
#                        linAssetPrices,
#                        linTime))
#                        
#PORTFOLIO HOLDING TRADERS
#exper.append(DAExperiment("results/da_experiments/mixedLmsrTraders1", 
#                        assetPrices, 
#                        interestRates, 
#                        mixedLmsrTraders1,
#                        [call_atm, call_otm, call_itm], 
#                        numTraders, 
#                        linAssetPrices,
#                        linTime))
#
#exper.append(DAExperiment("results/da_experiments/mixedLmsrTraders2", 
#                        assetPrices, 
#                        interestRates, 
#                        mixedLmsrTraders2,
#                        [call_atm, call_otm, call_itm], 
#                        numTraders, 
#                        linAssetPrices,
#                        linTime))
#
#exper.append(DAExperiment("results/da_experiments/mixedLmsrTraders3", 
#                        assetPrices, 
#                        interestRates, 
#                        mixedLmsrTraders3,
#                        [call_atm, call_otm, call_itm], 
#                        numTraders, 
#                        linAssetPrices,
#                        linTime))
##
#exper.append(DAExperiment("results/da_experiments/mixedLmsrTraders4", 
#                        assetPrices, 
#                        interestRates, 
#                        mixedLmsrTraders4,
#                        [call_atm, call_otm, call_itm], 
#                        numTraders, 
#                        linAssetPrices,
#                        linTime))
#MIXED TRADERS
#exper.append(DAExperiment("results/da_experiments/mixedAllTraders", 
#                        assetPrices, 
#                        interestRates, 
#                        mixedAllTraders,
#                        [call_atm, call_otm, call_itm], 
#                        numTraders, 
#                        linAssetPrices,
#                        linTime))
                        
#exper.append(DAExperiment("results/da_experiments/mixedRiskNeutralTraders1", 
#                        assetPrices, 
#                        interestRates, 
#                        mixedRiskNeutralTraders1,
#                        [call_atm, call_otm, call_itm], 
#                        numTraders, 
#                        linAssetPrices,
#                        linTime))
##
#exper.append(DAExperiment("results/da_experiments/mixedAllTraders1", 
#                        assetPrices, 
#                        interestRates, 
#                        mixedTraders1,
#                        [call_atm, call_otm, call_itm], 
#                        numTraders, 
#                        linAssetPrices,
#                        linTime))
#                        
#exper.append(DAExperiment("results/da_experiments/mixedMoreRiskAverseTraders1", 
#                        assetPrices, 
#                        interestRates, 
#                        mixedTraders2,
#                        [call_atm, call_otm, call_itm], 
#                        numTraders, 
#                        linAssetPrices,
#                        linTime))



for da_exp in exper:
    try:
        da_exp.start()
        #pass
    except:
        print "ERROR:", sys.exc_info()[0] 

#assetPrices, interestRates, traders, options, numTraders, linAssets, linTime):
#mechanisms
#
#da=DirectDASimulator('test', assetPrices, interestRates, mixedLmsrLinTraders4, call_atm, numTraders)
#plotDf=da.simulate()
#plotDf.plot(y=['BLSPrice', 'DAPrice', 'rejected_bid_max','rejected_ask_min'])
#plotDf.to_excel('results/da_experiments/lmsr_degen/mixedLmsrTraders1_Market.xls')

#plotDf=da.simulateVolCurve(linAssetPrices)
#plotDf.plot(x='Strikes', y='ImpVol')
#
#plotDf=da.simulateBSDelta(linAssetPrices)
#plotDf.plot(x='AssetPrice', y=['DA_Delta', 'BLS_Delta'])

#plotDf=da.simulateBSDeltaWithTime(linTime)
#plotDf.plot(x='TimeToMaturity', y=['DA_Delta', 'BLS_Delta'])
#
#plotDf=da.simulateBSGamma(linAssetPrices)
#plotDf.plot(x='AssetPrice', y=['DA_Gamma', 'BLS_Gamma'])

#plotDf=da.simulateBSGammaWithTime(linTime)
#plotDf.plot(x='TimeToMaturity', y=['DA_Gamma', 'BLS_Gamma'])
##
#plotDf=da.simulateBSTheta(linAssetPrices)
#plotDf.plot(x='AssetPrice', y=['DA_Theta', 'BLS_Theta'])

#plotDf=da.simulateBSThetaWithTime(linTime)
#plotDf.plot(x='TimeToMaturity', y=['DA_Theta', 'BLS_Theta'])

#jd=BrownianPricing(0.02,0.1)
#opt=CallOption(S0=100,K=100,r=0.02,sigma=0.01, T=1)
#expPricer=ExpPricing(jd,0.1)
#optPrices=expPricer.getPrices(opt, 100)
#print optPrices.head()