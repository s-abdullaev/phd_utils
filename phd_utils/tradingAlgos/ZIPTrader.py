# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 16:23:32 2015

@author: Desmond
"""

import matplotlib.pyplot as plt
from matplotlib import cm
import scipy.optimize as opt
import numpy as np

class ZIPTrader(object):
    def __init__(self, name, price):
        self.name=name
        self.tradeNum=0
        self.price=price
        self.curBid=price
        self.curAsk=price
        self.curBidMargin=np.random.uniform(0.1, 0.5)
        self.curAskMargin=np.random.uniform(0.1, 0.5)
        self.curBidGamma=0
        self.curAskGamma=0
        self.beta=np.random.uniform(0.1, 0.5) ## learning coef
        self.gamma=np.random.uniform(0.0,1.0) ## momentum on trend
    
    def setHatPrice(self, p):
        self.price=p
    
    def getLimitOrder(self, p, isBid):
        self.tradeNum+=1
        return {'type' : 'limit', 
                   'side' : 'bid' if isBid else 'ask', 
                    'quantity' : 5, 
                    'price' : p,
                    'trade_id' : self.name+str(self.tradeNum)}
    
    def submitLastQuote(self, lastQuote):
        if (lastQuote['status']=='accepted'):
            if self.curBid>lastQuote['price']:
                self.decreaseBid(lastQuote['price'])
            if lastQuote['side']=='ask' and self.curBid<lastQuote['price']:
                self.increaseBid(lastQuote['price'])
        else:
            if lastQuote['side']=='bid' and self.curBid<lastQuote['price']:
                self.increaseBid(lastQuote['price'])

        if (lastQuote['status']=='accepted'):
            if self.curAsk<lastQuote['price']:
                self.increaseAsk(lastQuote['price'])
            if lastQuote['side']=='bid' and self.curAsk>lastQuote['price']:
                self.decreaseAsk(lastQuote['price'])
        else:
            if lastQuote['side']=='ask' and self.curAsk<lastQuote['price']:
                self.decreaseAsk(lastQuote['price'])
    
    def getBid(self):
        return self.getLimitOrder(self.curBid, True)
        
    def getAsk(self):
        return self.getLimitOrder(self.curAsk, False)
    
    def decreaseBid(self, p):
        self.curBidGamma=self.gamma*self.curBidGamma+(1-self.gamma)*self.getDelta(p, False)
        self.curBidMargin=(self.curBid+self.curBidGamma)/self.price-1
        self.curBid=self.price*(1+self.curBidMargin)
    
    def increaseBid(self, p):
        bidGamma=self.gamma*self.curBidGamma+(1-self.gamma)*self.getDelta(p, True)
        bidMargin=(self.curBid+bidGamma)/self.price-1
        m=(1+bidMargin)
        #if m<=1:
        self.curBidGamma=bidGamma
        self.curBidMargin=bidMargin
        self.curBid=self.price*m
        
    def decreaseAsk(self, p):
        askGamma=self.gamma*self.curAskGamma+(1-self.gamma)*self.getDelta(p, False)
        askMargin=(self.curAsk+askGamma)/self.price-1
        m=(1+askMargin)
        #if m>=1:
        self.curAskGamma=askGamma
        self.curAskMargin=askMargin
        self.curAsk=self.price*m
    
    def increaseAsk(self, p):
        self.curAskGamma=self.gamma*self.curAskGamma+(1-self.gamma)*self.getDelta(p, True)
        self.curAskMargin=(self.curAsk+self.curAskGamma)/self.price-1
        self.curAsk=self.price*(1+self.curAskMargin)
    
    def getDelta(self, p, isUp):
        return self.beta*(self.getTau(p, isUp)-p)
    
    def getTau(self, p, isUp):
        if (isUp):
            R=np.random.uniform(1.0, 1.05)
            A=np.random.uniform(0.0, 0.05)
        else:
            R=np.random.uniform(0.95, 1)
            A=np.random.uniform(-0.05, 0)
            
        return R*p+A