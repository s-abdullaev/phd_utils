# -*- coding: utf-8 -*-
"""
Created on Thu Jul 09 02:38:33 2015

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

class DirectDA(object):
    #sm allocation rule
    def clearOrders(self, orders):
        numOrders=len(orders)
        bounds=[(0.0,1.0) for i in range(numOrders)]
                   
        b=orders['price'].values
        q=orders['quantity'].values
        c=-1*b*q
        A=np.zeros([2,numOrders])
        A[0]=-1*q
        b=np.zeros([2,1])
        res=optim.linprog(c, A_eq=A, b_eq=b, bounds=bounds, options={'disp':True})
        
        orders['accepted']=np.round(res.x, 4)
        
        return orders
    
    #multi-unit mcafee rule        
    def getPrice(self, orders):
        offbids=orders[(orders.accepted == 0) & (orders.quantity > 0)]
        offasks=orders[(orders.accepted == 0) & (orders.quantity < 0)]
        
        #can also use idxmax
        #offbids.ix[offbids.idxmax()['b']]['b']
        if len(offbids)>0:
            max_off_bid=offbids.ix[offbids.price.argmax()]['price']
        else:
            max_off_bid=orders[(orders.accepted > 0) & (orders.quantity > 0)]['price'].min()
            
        if len(offasks)>0:
            min_off_ask=offasks.ix[offasks.price.argmin()]['price']
        else:
            min_off_ask=orders[(orders.accepted > 0) & (orders.quantity < 0)]['price'].max()
        
        return 0.5*(max_off_bid+min_off_ask)
    
    def getVolume(self, orders):
        clrBids=orders[(orders.accepted > 0) & (orders.quantity > 0)]
        clrAsks=orders[(orders.accepted > 0) & (orders.quantity < 0)]
        
        volBids=clrBids['quantity'].sum()
        volAsks=abs(clrAsks['quantity'].sum())
        
        return min([volBids, volAsks])
        
    def getErrEfficiency(self, orders, volume):
        rejOrder=orders[(orders.accepted>0) & (orders.accepted<1)]
        if not rejOrder.empty:
            effErr=abs(rejOrder.accepted.values[0] * rejOrder.quantity.values[0])
            return effErr/(volume+effErr)
        else:
            return 0
    
    def getBudgetBalance(self, orders, price):
        rejOrder=orders[(orders.accepted>0) & (orders.accepted<1)]
        if not rejOrder.empty:
            return rejOrder.accepted.values[0] * rejOrder.quantity.values[0] * price
        else:
            return 0

class DirectDASimulator(object):
    def __init__(self, name, assetPrices, interestRates, traders, option, numOrders):
        self.name=name
        self.assetPrices=assetPrices
        self.interestRates=interestRates
        self.traders=traders
        self.option=option
        self.numOrders=numOrders
        self.mechanism=DirectDA()
        
    def simulate(self, save=True):
        opt=copy.copy(self.option)
        mechanism=self.mechanism
        
        plotDf=pd.DataFrame(np.zeros([opt.daysToMaturity(), 7]), columns=['DAPrice', 'BLSPrice', 'Volume', 'AssetPrice', 'InterestRate', 'EffErr', 'BB'])
        plotDf['AssetPrice']=self.assetPrices.values
        plotDf['InterestRate']=self.interestRates.values

        
        steps=np.linspace(opt.T, 0, opt.daysToMaturity())
        for i, t, p, r in zip(range(opt.daysToMaturity()), steps, self.assetPrices[0].values, self.interestRates.values):
            opt.T=t
            opt.S0=p    
            opt.r=r
            
            orders=self.traders.getOrders(opt, self.numOrders)
            orders=mechanism.clearOrders(orders)
            
            plotDf.ix[i]['DAPrice']=mechanism.getPrice(orders)
            plotDf.ix[i]['BLSPrice']=opt.blsPrice()    
            plotDf.ix[i]['InterestRate']=opt.r
            plotDf.ix[i]['Volume']=mechanism.getVolume(orders)
            plotDf.ix[i]['EffErr']=mechanism.getErrEfficiency(orders, plotDf.ix[i]['Volume'])
            plotDf.ix[i]['BB']=mechanism.getBudgetBalance(orders, plotDf.ix[i]['DAPrice'])
            
            print i
        
        if save:
            plotDf.to_excel('results/%s.xls' % self.name)

        return plotDf
        
#r=0.01
#sigma=0.5
#arrRate=4
#jumpMu=0.02
#jumpSigma=0.05
#
#assetMdl=JumpDiffPricing(r, sigma, arrRate, jumpMu, jumpSigma)
#opt=CallOption(S0=100,K=100,r=r,sigma=sigma, T=0.1)
#
#
#ziPricer=ZIPricing(assetMdl)
#
#
#rndModel=RandomQuantity((-2000,2000))
#linModel=LinearQuantity((-200,1000,500,1000))
#
#trader=DATrader()
#mechanism=DirectDA()
#
#steps=np.linspace(opt.T, 0, opt.daysToMaturity())
#assetPrices=assetMdl.generate(100, 1, opt.daysToMaturity(), True).T
#
#plotDf=pd.DataFrame(np.zeros([opt.daysToMaturity(), 4]), columns=['DAPrice', 'BLSPrice', 'Volume', 'AssetPrice'])
#
#plotDf['AssetPrice']=assetPrices.values
#for i, t, p in zip(range(opt.daysToMaturity()), steps, assetPrices[0].values):
#    opt.T=t
#    opt.S0=p    
#        
#    orders=trader.getOrders(opt, 100, QuantityModel=rndModel, AssetPricingModel=assetMdl)
#    orders=mechanism.clearOrders(orders)
#    plotDf.ix[i]['DAPrice']=mechanism.getPrice(orders)
#    plotDf.ix[i]['Volume']=mechanism.getVolume(orders)
#    plotDf.ix[i]['BLSPrice']=opt.blsPrice()
#    print i
#
#plotDf.plot(y=['DAPrice','BLSPrice'])