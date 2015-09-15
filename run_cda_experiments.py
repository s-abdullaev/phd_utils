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
from phd_utils.tradingAlgos.CDATrader import *
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
interestRates=pd.Series(np.ones(call_atm.daysToMaturity())*r, name='InterestRate')

#proxy algorithms


#traders
traders=[]
traders.extend([CDATrader(i, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=monOptPricer, ProxyTradingModel=GarmanProxyAlgo(i)) for i in range(1,30)])
traders.extend([CDATrader(i, QuantityModel=rndModel, AssetPricingModel=brwnMdl, OptionPricingModel=monJdOptPricer, ProxyTradingModel=ZIPProxyAlgo(i)) for i in range(30,60)])
traders.extend([CDATrader(i, QuantityModel=rndModel, OptionPricingModel=expOptPricer, ProxyTradingModel=ZIPProxyAlgo(i)) for i in range(60,90)])

cda=OnlineDASimulator('test', assetPrices, interestRates, traders, call_atm)

df=cda.simulate()
df.plot(y=['BLSPrice', 'CDAHigh'])
