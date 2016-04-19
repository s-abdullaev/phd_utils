# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 05:01:48 2015

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
from phd_utils.mechanisms.online_models import *
from phd_utils.mechanisms.experiment import *
from phd_utils.tradingAlgos.CDATrader import *
from phd_utils.options.EuropeanCompoundOption import *
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

sigma_eps=0.0

r_mu=0.46
r_sigma=0.09
r_theta=0.46
r_arrRate=4
r_muLambda=0.1
r_sigmaLambda=0.2

risk_aversion=0.1
lmsr_liquidity=2500

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
linModel=LinearQuantity(equib_quant)
constModel=LinearQuantity(qnty_const)

#underlying market
assetPrices=pd.read_excel('data/brwn_assetPrices.xls')[0]
assetPrices=assetPrices.ix[:call_atm.daysToMaturity()-1]
interestRates=pd.Series(np.ones(call_atm.daysToMaturity())*r, name='InterestRate')

#traders
#bs traders
bsTraders=[CDATrader(i, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer, ProxyTradingModel=BSProxyAlgo(i)) for i in range(1,100)]

#all zip
zipTraders=[]
zipTraders.append(CDATrader(1, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer, ProxyTradingModel=ZIPProxyAlgo(1, beta=0.1, gamma=0.1)))
zipTraders.append(CDATrader(2, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer, ProxyTradingModel=ZIPProxyAlgo(2, beta=0.5, gamma=0.1)))
zipTraders.append(CDATrader(3, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer, ProxyTradingModel=ZIPProxyAlgo(3, beta=0.9, gamma=0.1)))
zipTraders.append(CDATrader(4, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer, ProxyTradingModel=ZIPProxyAlgo(4, beta=0.1, gamma=0.5)))
zipTraders.append(CDATrader(5, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer, ProxyTradingModel=ZIPProxyAlgo(5, beta=0.5, gamma=0.5)))
zipTraders.append(CDATrader(6, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer, ProxyTradingModel=ZIPProxyAlgo(6, beta=0.9, gamma=0.5)))
zipTraders.append(CDATrader(7, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer, ProxyTradingModel=ZIPProxyAlgo(7, beta=0.1, gamma=0.9)))
zipTraders.append(CDATrader(8, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer, ProxyTradingModel=ZIPProxyAlgo(8, beta=0.5, gamma=0.9)))
zipTraders.append(CDATrader(9, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer, ProxyTradingModel=ZIPProxyAlgo(9, beta=0.9, gamma=0.9)))
zipTraders.extend([CDATrader(i, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer, ProxyTradingModel=ZIPProxyAlgo(i)) for i in range(10,100)])

#all gd
gdTraders=[CDATrader(i, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer, ProxyTradingModel=GDProxyAlgo(i)) for i in range(1,10)]

#zip+gd
zipGdTrader=[]
zipGdTrader.extend([CDATrader(i, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer, ProxyTradingModel=ZIPProxyAlgo(i)) for i in range(1,70)])
zipGdTrader.extend([CDATrader(i, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer, ProxyTradingModel=GDProxyAlgo(i)) for i in range(71,100)])

#cop+inf+zip
copTraders=[]
copTraders.append(CDATrader(1, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=bsOptPricer, ProxyTradingModel=CopelandProxyAlgo(1,0.01)))
copTraders.append(CDATrader(2, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=bsOptPricer, ProxyTradingModel=CopelandProxyAlgo(2,0.05)))
copTraders.append(CDATrader(3, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=bsOptPricer, ProxyTradingModel=CopelandProxyAlgo(3,0.1)))
copTraders.append(CDATrader(4, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=bsOptPricer, ProxyTradingModel=CopelandProxyAlgo(4,0.5)))
copTraders.append(CDATrader(5, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=bsOptPricer, ProxyTradingModel=CopelandProxyAlgo(5,0.8)))
#copTraders.extend([CDATrader(i, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer, ProxyTradingModel=InformedProxyAlgo(i, call_atm.payoff(3563.57), 'bid')) for i in range(6,26)])
copTraders.extend([CDATrader(i, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer, ProxyTradingModel=ZIPProxyAlgo(i)) for i in range(6,100)])

#gar+zip
garTraders=[]
garTraders.append(CDATrader(1, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=bsOptPricer, ProxyTradingModel=GarmanProxyAlgo(1,1000,100)))
garTraders.append(CDATrader(2, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=bsOptPricer, ProxyTradingModel=GarmanProxyAlgo(2,500000,10000)))
garTraders.append(CDATrader(3, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=bsOptPricer, ProxyTradingModel=GarmanProxyAlgo(3,1000000,10000)))
garTraders.append(CDATrader(4, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=bsOptPricer, ProxyTradingModel=GarmanProxyAlgo(4,500000,50000)))
garTraders.append(CDATrader(5, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=bsOptPricer, ProxyTradingModel=GarmanProxyAlgo(5,1000000,100000)))
garTraders.append(CDATrader(6, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=bsOptPricer, ProxyTradingModel=GarmanProxyAlgo(6,1000000,1000000)))
garTraders.extend([CDATrader(i, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer, ProxyTradingModel=ZIPProxyAlgo(i)) for i in range(7,100)])

#mixed
mixedTraders=[]
mixedTraders.append(CDATrader(1, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=bsOptPricer, ProxyTradingModel=GarmanProxyAlgo(1,1000,100)))
mixedTraders.append(CDATrader(2, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=bsOptPricer, ProxyTradingModel=GarmanProxyAlgo(2,500000,10000)))
mixedTraders.append(CDATrader(3, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=bsOptPricer, ProxyTradingModel=GarmanProxyAlgo(3,1000000,10000)))
mixedTraders.append(CDATrader(4, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=bsOptPricer, ProxyTradingModel=GarmanProxyAlgo(4,500000,50000)))
mixedTraders.append(CDATrader(5, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=bsOptPricer, ProxyTradingModel=GarmanProxyAlgo(5,1000000,100000)))
mixedTraders.append(CDATrader(6, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=bsOptPricer, ProxyTradingModel=GarmanProxyAlgo(6,1000000,1000000)))
mixedTraders.append(CDATrader(10, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=bsOptPricer, ProxyTradingModel=CopelandProxyAlgo(7,0.01)))
mixedTraders.append(CDATrader(11, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=bsOptPricer, ProxyTradingModel=CopelandProxyAlgo(8,0.05)))
mixedTraders.append(CDATrader(12, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=bsOptPricer, ProxyTradingModel=CopelandProxyAlgo(9,0.1)))
mixedTraders.append(CDATrader(13, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=bsOptPricer, ProxyTradingModel=CopelandProxyAlgo(10,0.5)))
mixedTraders.append(CDATrader(14, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=bsOptPricer, ProxyTradingModel=CopelandProxyAlgo(11,0.8)))
mixedTraders.extend([CDATrader(i, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer, ProxyTradingModel=ZIPProxyAlgo(i)) for i in range(12,70)])
mixedTraders.extend([CDATrader(i, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer, ProxyTradingModel=GDProxyAlgo(i)) for i in range(71,100)])

#cda=OnlineDASimulator('test', assetPrices, interestRates, zipTraders, call_otm)
#
#df, traderDf, traderResultsDf=cda.simulate()
#df[:-1].plot(y=['BLSPrice', 'CDAHigh'])

#EXPERIMENTS
exper=[]

#BS TRADERS
#exper.append(CDAExperiment("results/cda_experiments/bsTraders", 
#                        assetPrices, 
#                        interestRates, 
#                        bsTraders,
#                        [call_atm, call_otm, call_itm]))

#ZIP TRADERS
#exper.append(CDAExperiment("results/cda_experiments/zipTraders1", 
#                        assetPrices, 
#                        interestRates, 
#                        zipTraders,
#                        [call_atm, call_otm, call_itm]))
#
##GD TRADERS
#exper.append(CDAExperiment("results/cda_experiments/gdTraders", 
#                        assetPrices, 
#                        interestRates, 
#                        gdTraders,
#                        [call_atm, call_otm, call_itm]))
#
##ZIP GD TRADERS
#exper.append(CDAExperiment("results/cda_experiments/zipGdTraders", 
#                        assetPrices, 
#                        interestRates, 
#                        zipGdTrader,
#                        [call_atm, call_otm, call_itm]))
#
##COP TRADERS
#exper.append(CDAExperiment("results/cda_experiments/copTraders", 
#                        assetPrices, 
#                        interestRates, 
#                        copTraders,
#                        [call_atm, call_otm, call_itm]))
##GAR TRADERS
exper.append(CDAExperiment("results/cda_experiments/garTraders2", 
                        assetPrices, 
                        interestRates, 
                        garTraders,
                        [call_atm, call_otm, call_itm]))

#MIXED TRADERS                        
#exper.append(CDAExperiment("results/cda_experiments/mixedTraders", 
#                        assetPrices, 
#                        interestRates, 
#                        mixedTraders,
#                        [call_atm, call_otm, call_itm]))

for da_exp in exper:
#    try:
    da_exp.start()
        #pass
#    except:
#        print "ERROR:", sys.exc_info()[0] 