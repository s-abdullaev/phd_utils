# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 02:35:05 2015

@author: Desmond
"""
from __future__ import division
import numpy as np
import pandas as pd
from numpy.random import randn

class BrownianPricing(object):
    def __init__(self, mu, sigma):
        self.mu=mu
        self.sigma=sigma
    
    def generate(self, S0, size, days, isAll=False):
        W=np.random.randn(size, days)
        dt=1/365.0
        logS0=np.log(S0)
        dlogS=(self.mu-0.5*self.sigma**2)*dt + self.sigma*np.sqrt(dt)*W
        logS=logS0+np.cumsum(dlogS,axis=1);
        S=np.exp(logS);
        if isAll:
            return pd.DataFrame(S, index=range(size), columns=range(days))
        else:
            return pd.Series(S[:,-1], name='GBMPrices')

class JumpDiffPricing(object):
    def __init__(self, mu, sigma, arrRate, jumpMu, jumpSigma):
        self.mu=mu
        self.sigma=sigma
        self.arrRate=arrRate
        self.jumpMu=jumpMu
        self.jumpSigma=jumpSigma
        
    def generate(self, S0, size, days, isAll=False):
        dt=1/365
        dS=np.zeros([size, days])
    
        for t in range(days):
            jumpnb=np.random.poisson(self.arrRate*dt, size)
            jump=np.random.normal(loc=self.jumpMu*dt*jumpnb,scale=0.0001+np.sqrt(jumpnb)*self.jumpSigma)
            dS[:,t]=self.mu*dt+self.sigma*np.sqrt(dt)*np.random.randn(size)+jump
        S=S0*(1+np.cumsum(dS, axis=1))
        
        if isAll:
            return pd.DataFrame(S, index=range(size), columns=range(days))
        else:
            return pd.Series(S[:,-1], name='JumpDiffPrices')

class VasicekPricing(object):
    def __init__(self,  mu, sigma, theta):
        self.mu=mu
        self.sigma=sigma
        self.theta=theta
    
    def generate(self, S0, size, days, isAll=False):
        dt=1/365
        S=np.zeros([size, days])
        
        for p in range(size):
            for t in range(days):
                if (t==0):
                    lastS=S0
                else:
                    lastS=S[p, t-1]
                W=randn()
                dS=self.theta*(self.mu-lastS)*dt + self.sigma*np.sqrt(dt)*W
                S[p,t]=lastS+dS
        if isAll:
            return pd.DataFrame(S, index=range(size), columns=range(days))
        else:
            return pd.Series(S[:,-1], name='VasicekPrices')

class VasicekJumpPricing(object):
    def __init__(self, mu, sigma, theta, arrRate, jumpMu, jumpSigma):
        self.mu=mu
        self.sigma=sigma
        self.theta=theta
        self.arrRate=arrRate
        self.jumpMu=jumpMu
        self.jumpSigma=jumpSigma

    def generate(self, S0, size, days, isAll=False):
        dt=1/365
        S=np.zeros([size, days])
        
        for p in range(size):
            for t in range(days):
                if (t==0):
                    lastS=S0
                else:
                    lastS=S[p, t-1]
                W=randn()

                jumpnb=np.random.poisson(self.arrRate*dt)
                jump=np.random.normal(loc=self.jumpMu*dt*jumpnb,scale=0.0001+np.sqrt(jumpnb)*self.jumpSigma)
                
                dS=self.theta*(self.mu-lastS)*dt + self.sigma*np.sqrt(dt)*W+jump
                S[p,t]=lastS+dS
        if isAll:
            return pd.DataFrame(S, index=range(size), columns=range(days))
        else:
            return pd.Series(S[:,-1], name='VasicekJumpPrices')