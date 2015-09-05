from __future__ import division
from math import *
import numpy as np
import pandas as pd
import scipy.stats as stats
import scipy.optimize as optim
import copy
import vollib.black_scholes.implied_volatility as iv
import vollib.black_scholes as bls
import vollib.black_scholes.greeks.analytical as greeks

def getImpVol(price, opt, prev_sigmas):
    def optPrice(curVol):
        return (price-bls.black_scholes('c', opt.S0, opt.K, opt.T, opt.r, curVol))**2
    v=optim.fminbound(optPrice, 0,10,maxfun=500, disp=0)
    prev_sigmas.append(v)
    pSigmas=np.array(prev_sigmas)    
    countNonZeros=len(pSigmas[pSigmas>0])
    
    return sum(prev_sigmas)/countNonZeros

OPTION_PORTFOLIOS=pd.DataFrame({'Short Call':	[-1, 0, 0, 0, 0, 0],
                         'Long Call': [1, 0, 0, 0, 0, 0],
                         'Long Put': [0, 1, 0, 0, 0, 0],
                         'Short Put': [0, -1, 0, 0, 0, 0],
                         'Bull Call Spread': [0, 0, -1, 0, 1, 0],   
            		  'Bull Put Spread': [0, 0, 0, 1, 0, -1],
                         'Bear Call Spread': [0, 0, 1, 0, -1, 0],
                         'Bear Put Spread': [0, 0, 0, -1, 0, 1],
                         'Bear Put Spread': [0, 0, 0, -1, 0, 1],
            		  'Butterfly Call Spread':	[-2, 0, 1, 0, 1, 0],
                         'Butterfly Put Spread': [0,-2, 0, 1, 0, 1],
                         'Long Call Ladder':[-1, 0, -1, 0, 1, 0],
                         'Short Call Ladder': [1, 0, 0, 1, 0, -1],
                         'Long Put Ladder': [0, -1, 0, -1, 0, 1],
                         'Short Put Ladder':	[0, 1, 0, 1, 0, -1],
                         'Iron Butterfly': [-1, -1, 1, 1, 0, 0],
                         'Long Straddle': [1, 1, 0, 0, 0, 0],
                         'Short Straddle': [-1, -1, 0, 0, 0, 0],
                         'Long Strangle': [0, 0, 1, 1, 0, 0],
            		  'Short Strangle': [0, 0, -1, -1, 0, 0],
            		  'Strip': [1, 2, 0, 0, 0, 0],
                         'Strap': [2, 1, 0, 0, 0, 0]}).T
                         
OPTION_PORTFOLIOS.columns=['ATM_call', 'ATM_put', 'OTM_call', 'OTM_put', 'ITM_call', 'ITM_put']

class OptionContract(object):
    def __init__(self, **kwargs):
        self.K=100
        self.isLong=True
        self.S0=100.0
        self.r=0.05
        self.T=1
        self.sigma=0.02
        self.__dict__.update(kwargs)
        
    def daysToMaturity(self):
        return int(np.floor(self.T*365))
    
    def discount(self, val):
        return val*np.exp(-self.r*self.T)

    def payoff(self, St):
        val=np.minimum(np.maximum(St-self.K,0), self.S0)
        if not self.isLong: val=-val
        return val

    def discK(self):
        return self.discount(self.K)

    def d1(self):
        return (np.log(self.S0 / self.K) + (self.r + 0.5*self.sigma**2) * self.T) / (self.sigma * np.sqrt(self.T))

    def d2(self):
        return (np.log(self.S0 / self.K) + (self.r - 0.5*self.sigma**2) * self.T) / (self.sigma * np.sqrt(self.T))

    def blsPrice(self):
        return self.S0 * stats.norm.cdf(self.d1()) - self.K * self.discount(stats.norm.cdf(self.d2()))
    
    def delta(self):
        return stats.norm.cdf(self.d1())
        
    def getImpVol(self, price):
        print price, self.blsPrice()
        def optPrice(curVol):
            if curVol<0: return 1000
            return (price-bls.black_scholes('c', self.S0, self.K, self.T, self.r, curVol))**2
        v=optim.fmin(optPrice, self.sigma, maxfun=500, disp=0)[0]
        return v
                
    def gamma(self):
        NPrime=((2*np.pi)**(-1/2))*np.exp(-0.5*(self.d1())**2)
        return (NPrime/(self.S0*self.sigma*self.T**(1/2)))
    
    def theta(self):
        NPrime=((2*np.pi)**(-1/2))*np.exp(-0.5*(self.d1())**2)
        return (NPrime)*(-self.S0*self.sigma*0.5/np.sqrt(self.T))-self.r*self.K * np.exp(-self.r * self.T) * stats.norm.cdf(self.d2())


class CallOption(OptionContract):
    pass

class PutOption(OptionContract):
    def payoff(self, St):
        val=np.minimum(np.maximum(self.K-St,0), self.discK())
        if not self.isLong: val=-val
        return val
        
    def blsPrice(self):
        return self.K * self.discount(stats.norm.cdf(-self.d2()))-self.S0 * stats.norm.cdf(-self.d1())
    
    def delta(self):
        return -stats.norm.cdf(-self.d1())

class OptionPortfolio(object):
    def __init__(self, atm_call, atm_put, eps, port_qnties):
        self.portfolio=[]        
        if port_qnties['ATM_call']:
            opt=copy.copy(atm_call)
            opt.isLong = True if port_qnties['ATM_call']>0 else False
            for o in [opt]*abs(port_qnties['ATM_call']):
                self.portfolio.append(o)
                
        if port_qnties['ATM_put']:
            opt=copy.copy(atm_put)
            opt.isLong = True if port_qnties['ATM_put']>0 else False
            for o in [opt]*abs(port_qnties['ATM_put']):
                self.portfolio.append(o)
        
        if port_qnties['ITM_call']:
            opt=copy.copy(atm_call)
            opt.K-=eps
            opt.isLong = True if port_qnties['ITM_call']>0 else False
            for o in [opt]*abs(port_qnties['ITM_call']):
                self.portfolio.append(o)
                
        if port_qnties['ITM_put']:
            opt=copy.copy(atm_put)
            opt.K+=eps
            opt.isLong = True if port_qnties['ITM_put']>0 else False
            for o in [opt]*abs(port_qnties['ITM_put']):
                self.portfolio.append(o)
        
        if port_qnties['OTM_call']:
            opt=copy.copy(atm_call)
            opt.K+=eps
            opt.isLong = True if port_qnties['OTM_call']>0 else False
            for o in [opt]*abs(port_qnties['OTM_call']):
                self.portfolio.append(o)
                
        if port_qnties['OTM_put']:
            opt=copy.copy(atm_put)
            opt.K-=eps
            opt.isLong = True if port_qnties['OTM_put']>0 else False
            for o in [opt]*abs(port_qnties['OTM_put']):
                self.portfolio.append(o)
    
    def payoff(self, St):
        return np.sum(opt.payoff(St) for opt in self.portfolio)
        
    def blsPrice(self):
        return np.sum(opt.blsPrice() for opt in self.portfolio)
    
    def delta(self):
        return np.sum(opt.delta() for opt in self.portfolio)
    
    def gamma(self):
        return np.sum(opt.gamma() for opt in self.portfolio)
        
    def theta(self):
        return np.sum(opt.theta() for opt in self.portfolio)