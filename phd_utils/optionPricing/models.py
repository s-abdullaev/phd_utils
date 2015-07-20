# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 02:23:14 2015

@author: Desmond
"""
from __future__ import division
import numpy as np
import pandas as pd
import copy
from phd_utils.options import *
from phd_utils.assetPricing import models as assetPricing
import scipy.optimize as optim
import scipy.stats as stats
import matplotlib.pyplot as plt

class ZIPricing(object):
    def __init__(self, assetPricingModel):
        self.model=assetPricingModel
    
    def getPrices(self, opt, size):
        if opt.T==0: 
            return pd.Series([opt.payoff(opt.S0)]*size, name='prices')

        days=int(np.floor(opt.T*365))
        prices=self.model.generate(opt.S0, size, days)
        optPrices=prices.apply(lambda x: opt.payoff(x))
        optPrices.name='prices'
        return optPrices
#jd=assetPricing.BrownianPricing(100,0.02,0.1)
#opt=eurOpt.CallOption(S0=100,K=100,r=0.02,sigma=0.01, T=1)
#ziPricer=ZIPricing(jd, opt)
#optPrices=ziPricer.getPrices(100)
#optPrices.hist()

class BSPricing(object):
    def __init__(self, ret, sigma):
        self.ret=ret
        self.sigma=sigma
    
    def getPrices(self, opt, size):
        if opt.T==0: 
            return pd.Series([opt.payoff(opt.S0)]*size, name='prices')

        basePrices=[]
        for r,sig in zip(self.ret, self.sigma):
            self.option=copy.deepcopy(opt)
            self.option.S0=S0
            self.option.r=r
            self.option.sigma=sig
            basePrices.append(self.option.blsPrice())
        return pd.Series(np.random.choice(basePrices,replace=True, size=size), name='prices')

class MonteCarloPricing(object):
    def __init__(self, assetPricingModel, ntrials):
        self.model=assetPricingModel
        self.ntrials=ntrials
    
    def getPrices(self, opt, size):
        if opt.T==0: 
            return pd.Series([opt.payoff(opt.S0)]*size, name='prices')

        optPrices=[]
        for i in range(size):
            days=int(np.floor(opt.T*365))
            curPrices=self.model.generate(opt.S0, self.ntrials, days)
            curOptPrices=curPrices.apply(lambda x: opt.payoff(x))
            
            optPrices.append(curOptPrices.mean())
        return pd.Series(optPrices, name='prices')
#jd=assetPricing.BrownianPricing(100,0.02,0.1)
#opt=eurOpt.CallOption(S0=100,K=100,r=0.02,sigma=0.01, T=1)
#mcPricer=MonteCarloPricing(jd, opt, 100)
#optPrices=mcPricer.getPrices(100)
#optPrices.hist()

class DeltaHedgePricing(object):
    def __init__(self, assetPricingModel, ntrials, premium):
        self.model=assetPricingModel
        self.ntrials=ntrials
        self.premium=premium if premium else self.option.blsPrice()
    
    def getPrices(self, opt, size):
        if opt.T==0: 
            return pd.Series([opt.payoff(opt.S0)]*size, name='prices')

        dt=1/365
        days=int(np.floor(self.option.T*365))
        steps=np.linspace(self.option.T, 0, days)
        self.initOptParams=copy.copy(opt.__dict__)
        self.option=copy.deepcopy(opt)
        
        optPrices=[]
        for i in range(size):
            #print self.option.S0
            curPrices=self.model.generate(opt.S0, self.ntrials, days, True).T.values
            curBank=np.zeros([days, self.ntrials])
            curDelta=np.zeros([days, self.ntrials])
            curBank[0]=np.ones(self.ntrials)*(self.premium-self.option.S0*self.option.delta())
            curDelta[0]=np.ones(self.ntrials)*self.option.delta()
            for j in range(1,days):
                p=curPrices[j]
                t=steps[j]
                self.option.T=t
                self.option.S0=p
                curDelta[j]=self.option.delta()
                dDelta=(curDelta[j]-curDelta[j-1])*p
                
                curBank[j]=np.exp(self.option.r*dt)*curBank[j-1]-dDelta
            self.option.__dict__.update(self.initOptParams)           
            curBank[-1]=curBank[-1]+curDelta[-1]*curPrices[-1]-[self.option.payoff(x) for x in curPrices[-1]]
            optPrices.append(self.premium-np.mean(curBank[-1]))
            
        return pd.Series(optPrices, name='prices')
#jd=assetPricing.BrownianPricing(100,0.02,0.1)
#opt=eurOpt.CallOption(S0=100,K=100,r=0.02,sigma=0.01, T=1)
#dhPricer=DeltaHedgePricing(jd, opt, 100,None)
#optPrices=dhPricer.getPrices(100)
#optPrices.hist()

class ExpPricing(object):
    def __init__(self, assetPricingModel, riskAverse):
        self.model=assetPricingModel
        self.riskAverse=riskAverse
    
    def getPrices(self, opt, size):
        if opt.T==0: 
            return pd.Series([opt.payoff(opt.S0)]*size, name='prices')

        days=opt.daysToMaturity()
        optPrices=[]
        def u(x):
            return (1-np.exp(-self.riskAverse*x))/self.riskAverse
        
        def expectedUtil(price):
            return np.mean(u(np.exp(opt.r*opt.T)*price-curOptPrices))
        
        for i in range(size):
            curPrices=self.model.generate(opt.S0, 1000, days)
            curOptPrices=curPrices.apply(lambda x: opt.payoff(x))        
            p=optim.fsolve(expectedUtil, opt.blsPrice())
            optPrices.append(p)
        return pd.Series(optPrices, name='prices')
        
#jd=assetPricing.BrownianPricing(100,0.02,0.1)
#opt=eurOpt.CallOption(S0=100,K=100,r=0.02,sigma=0.01, T=1)
#expPricer=ExpPricing(jd, opt, 0.1)
#optPrices=expPricer.getPrices(100)
#optPrices.hist()
        
class LMSRPricing(object):
    def __init__(self, assetPricingModel, ntrials, liquidity, portfolio):
        self.model=assetPricingModel
        self.ntrials=ntrials
        self.portfolio=portfolio
        self.b=liquidity
        
    def payoff(self, portfolio, rangeOfEvents):
        return np.array([portfolio.payoff(St) for St in rangeOfEvents])
        
    def lmsr(self, vals):
        return self.b * np.log(sum(np.exp(vals/self.b)))

    def getPrices(self, opt, size):
        if opt.T==0: 
            return pd.Series([opt.payoff(opt.S0)]*size, name='prices')

        days=opt.daysToMaturity()
        optPrices=[]        
        for i in range(size):
            rangeOfEvents=self.model.generate(opt.S0, self.ntrials, days)
            rangeOfEvents=np.linspace(rangeOfEvents.min(),rangeOfEvents.max(), 20)
            
            tempPort=copy.deepcopy(self.portfolio)
            tempPort.portfolio.append(opt)
            
            tempPayoffs=self.payoff(tempPort, rangeOfEvents)
            curPayoffs=self.payoff(self.portfolio, rangeOfEvents)        
            
            optPrices.append(self.lmsr(tempPayoffs)-self.lmsr(curPayoffs))
        return pd.Series(optPrices, name='prices')

#optATM=CallOption(S0=100,K=100,r=0.02,sigma=0.5, T=1, isLong=False)
#optOTM=CallOption(S0=100,K=110,r=0.02,sigma=0.5, T=1)
#optITM=CallOption(S0=100,K=90,r=0.02,sigma=0.5, T=1)
#optATM2=CallOption(S0=100,K=50,r=0.02,sigma=0.5, T=1)
#
#optPort=OptionPortfolio(portfolio=[optOTM, optITM, optATM, optATM], name='Butterfly')
#
#jd=assetPricing.BrownianPricing(100,0.02,0.5)
#lmsrPricer=LMSRPricing(jd, optATM2, 100, 2500, optPort)
#optPrices=lmsrPricer.getPrices(100)
#print optPrices