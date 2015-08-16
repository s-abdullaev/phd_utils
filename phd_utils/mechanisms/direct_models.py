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
from scipy.misc import derivative
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
            if max_off_bid<=0:
                max_off_bid=orders[(orders.accepted > 0) & (orders.quantity > 0)]['price'].min()
        else:
            max_off_bid=orders[(orders.accepted > 0) & (orders.quantity > 0)]['price'].min()
            
        if len(offasks)>0:
            min_off_ask=offasks.ix[offasks.price.argmin()]['price']
            if min_off_ask<=0:
                min_off_ask=orders[(orders.accepted > 0) & (orders.quantity < 0)]['price'].max()
        else:
            min_off_ask=orders[(orders.accepted > 0) & (orders.quantity < 0)]['price'].max()
        
        return 0.5*(max_off_bid+min_off_ask)
    
    def getVolume(self, orders):
        clrBids=orders[(orders.accepted > 0) & (orders.quantity > 0)]
        clrAsks=orders[(orders.accepted > 0) & (orders.quantity < 0)]
        
        volBids=clrBids['quantity'].sum()
        volAsks=abs(clrAsks['quantity'].sum())
        
        return min([volBids, volAsks])
        
    def getPriceStats(self, orders):
        price_stats={}
        accepted_bids=orders[(orders.accepted == 1) & (orders.quantity > 0)].price
        accepted_asks=orders[(orders.accepted == 1) & (orders.quantity < 0)].price
        
        rejected_bids=orders[(orders.accepted < 1) & (orders.quantity > 0)].price
        rejected_asks=orders[(orders.accepted < 1) & (orders.quantity < 0)].price
        
        price_stats['accepted_bid_max']=accepted_bids.max()
        price_stats['accepted_bid_min']=accepted_bids.min()
        price_stats['accepted_bid_avg']=np.mean(accepted_bids)
        price_stats['accepted_bid_std']=np.std(accepted_bids)
        
        price_stats['accepted_ask_max']=accepted_asks.max()
        price_stats['accepted_ask_min']=accepted_asks.min()
        price_stats['accepted_ask_avg']=np.mean(accepted_asks)
        price_stats['accepted_ask_std']=np.std(accepted_asks)
        
        price_stats['rejected_bid_max']=rejected_bids.max()
        price_stats['rejected_bid_min']=rejected_bids.min()
        price_stats['rejected_bid_avg']=np.mean(rejected_bids)
        price_stats['rejected_bid_std']=np.std(rejected_bids)
        
        price_stats['rejected_ask_max']=rejected_asks.max()
        price_stats['rejected_ask_min']=rejected_asks.min()
        price_stats['rejected_ask_avg']=np.mean(rejected_asks)
        price_stats['rejected_ask_std']=np.std(rejected_asks)
        
        return price_stats
        
    def getPriceStatCols(self):
        price_stats_cols=['accepted_bid_max',
                          'accepted_bid_min', 
                          'accepted_bid_avg', 
                          'accepted_bid_std',
                          'accepted_ask_max',
                          'accepted_ask_min',
                          'accepted_ask_avg',
                          'accepted_ask_std',
                          'rejected_bid_max',
                          'rejected_bid_min',
                          'rejected_bid_avg',
                          'rejected_bid_std',
                          'rejected_ask_max',
                          'rejected_ask_min',
                          'rejected_ask_avg',
                          'rejected_ask_std']
        return price_stats_cols
        
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
        
    def simulate(self):
        opt=copy.copy(self.option)
        mechanism=self.mechanism
        cols=['DAPrice', 'BLSPrice', 'Volume', 'AssetPrice', 'InterestRate', 'EffErr', 'BB']
        cols+=mechanism.getPriceStatCols()
        
        plotDf=pd.DataFrame(np.zeros([opt.daysToMaturity(), 23]), columns=cols)
        plotDf['AssetPrice']=self.assetPrices.values
        plotDf['InterestRate']=self.interestRates.values

        
        steps=np.linspace(opt.T, 0, opt.daysToMaturity())
        for i, t, p, r in zip(range(opt.daysToMaturity()), steps, self.assetPrices.values, self.interestRates.values):
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
            
            priceStats=mechanism.getPriceStats(orders)
            for k in mechanism.getPriceStatCols():
                plotDf.ix[i][k]=priceStats[k]
            
            print i
        return plotDf
    
    def simulateBSDelta(self, assetPrices):
        opt=copy.copy(self.option)
        opt2=copy.copy(self.option)
        mechanism=self.mechanism
        
        plotDf=pd.DataFrame(np.zeros([len(assetPrices), 3]), columns=['AssetPrice', 'DA_Delta', 'BLS_Delta'])
        plotDf['AssetPrice']=assetPrices.values
        
        for i, p in enumerate(assetPrices.values):
            opt.S0=p
            opt2.S0=p
        
            orders=self.traders.getOrders(opt, self.numOrders)
            orders=mechanism.clearOrders(orders)
            
            curOptPrice=mechanism.getPrice(orders)
            opt2.sigma=opt.getImpVol(curOptPrice)
            
            plotDf.ix[i]['DA_Delta']=opt2.delta()
            plotDf.ix[i]['BLS_Delta']=opt.delta()
            
            print i
     
        return plotDf
    
    def simulateBSDeltaWithTime(self, timeSteps):
        opt=copy.copy(self.option)
        opt2=copy.copy(self.option)
        mechanism=self.mechanism
        
        plotDf=pd.DataFrame(np.zeros([len(timeSteps), 3]), columns=['TimeToMaturity', 'DA_Delta', 'BLS_Delta'])
        plotDf['TimeToMaturity']=timeSteps
        
        for i, p in enumerate(timeSteps):
            opt.T=p
            opt2.T=p
        
            orders=self.traders.getOrders(opt, self.numOrders)
            orders=mechanism.clearOrders(orders)
            
            curOptPrice=mechanism.getPrice(orders)
            opt2.sigma=opt.getImpVol(curOptPrice)
            
            plotDf.ix[i]['DA_Delta']=opt2.delta()
            plotDf.ix[i]['BLS_Delta']=opt.delta()
            
            print i
     
        return plotDf
    
    def simulateBSGamma(self, assetPrices):
        opt=copy.copy(self.option)
        opt2=copy.copy(self.option)
        mechanism=self.mechanism
        
        plotDf=pd.DataFrame(np.zeros([len(assetPrices), 3]), columns=['AssetPrice', 'DA_Gamma', 'BLS_Gamma'])
        plotDf['AssetPrice']=assetPrices.values
        
        for i, p in enumerate(assetPrices.values):
            opt.S0=p
            opt2.S0=p
        
            orders=self.traders.getOrders(opt, self.numOrders)
            orders=mechanism.clearOrders(orders)
            
            curOptPrice=mechanism.getPrice(orders)
            opt2.sigma=opt.getImpVol(curOptPrice)
            
            plotDf.ix[i]['DA_Gamma']=opt2.gamma()
            plotDf.ix[i]['BLS_Gamma']=opt.gamma()
            
            print i
     
        return plotDf
    
    def simulateBSGammaWithTime(self, timeSteps):
        opt=copy.copy(self.option)
        opt2=copy.copy(self.option)
        mechanism=self.mechanism
        
        plotDf=pd.DataFrame(np.zeros([len(timeSteps), 3]), columns=['TimeToMaturity', 'DA_Gamma', 'BLS_Gamma'])
        plotDf['TimeToMaturity']=timeSteps
        
        for i, p in enumerate(timeSteps):
            opt.T=p
            opt2.T=p
        
            orders=self.traders.getOrders(opt, self.numOrders)
            orders=mechanism.clearOrders(orders)
            
            curOptPrice=mechanism.getPrice(orders)
            opt2.sigma=opt.getImpVol(curOptPrice)
            
            plotDf.ix[i]['DA_Gamma']=opt2.gamma()
            plotDf.ix[i]['BLS_Gamma']=opt.gamma()
            
            print i     
        return plotDf
    
    def simulateBSTheta(self, assetPrices):
        opt=copy.copy(self.option)
        opt2=copy.copy(self.option)
        mechanism=self.mechanism
        
        plotDf=pd.DataFrame(np.zeros([len(assetPrices), 3]), columns=['AssetPrice', 'DA_Theta', 'BLS_Theta'])
        plotDf['AssetPrice']=assetPrices.values
        
        for i, p in enumerate(assetPrices.values):
            opt.S0=p
            opt2.S0=p
            
            orders=self.traders.getOrders(opt, self.numOrders)
            orders=mechanism.clearOrders(orders)
                
            opt2.sigma=opt.getImpVol(mechanism.getPrice(orders))
            
            plotDf.ix[i]['DA_Theta']=opt2.theta()
            plotDf.ix[i]['BLS_Theta']=opt.theta()
            
            print i
     
        return plotDf
    
    def simulateBSThetaWithTime(self, timeSteps):
        opt=copy.copy(self.option)
        opt2=copy.copy(self.option)
        mechanism=self.mechanism
        
        plotDf=pd.DataFrame(np.zeros([len(timeSteps), 3]), columns=['TimeToMaturity', 'DA_Theta', 'BLS_Theta'])
        plotDf['TimeToMaturity']=timeSteps
        
        for i, p in enumerate(timeSteps):
            opt.T=p
            opt2.T=p
        
            orders=self.traders.getOrders(opt, self.numOrders)
            orders=mechanism.clearOrders(orders)
            
            curOptPrice=mechanism.getPrice(orders)
            opt2.sigma=opt.getImpVol(curOptPrice)
            
            plotDf.ix[i]['DA_Theta']=opt2.theta()
            plotDf.ix[i]['BLS_Theta']=opt.theta()
            
            print i     
        return plotDf
    
    def simulateVolCurve(self, strikes):
        opt=copy.copy(self.option)
        mechanism=self.mechanism
        
        plotDf=pd.DataFrame(np.zeros([len(strikes), 2]), columns=['Strikes', 'ImpVol'])
        plotDf['Strikes']=strikes
        
        for i, p in enumerate(strikes):
            opt.K=p
            opt2=copy.copy(opt)
            
            orders=self.traders.getOrders(opt, self.numOrders)
            orders=mechanism.clearOrders(orders)
            
            plotDf.ix[i]['ImpVol']=opt2.getImpVol(mechanism.getPrice(orders))

            print i     
        return plotDf
    
    def simulateDelta(self, assetPrices):
        opt=copy.copy(self.option)
        mechanism=self.mechanism
        
        plotDf=pd.DataFrame(np.zeros([len(assetPrices), 3]), columns=['AssetPrice', 'DA_Delta', 'BLS_Delta'])
        plotDf['AssetPrice']=assetPrices.values
        
        def optPrice(assetPrice):
            opt.S0=assetPrice
            orders=self.traders.getOrders(opt, self.numOrders)
            orders=mechanism.clearOrders(orders)
            
            return np.mean(mechanism.getPrice(orders))
        
        for i, p in enumerate(assetPrices.values):
            plotDf.ix[i]['DA_Delta']=derivative(optPrice, x0=p,dx=20)
            
            opt.S0=p            
            plotDf.ix[i]['BLS_Delta']=opt.delta()
            
            print i
     
        return plotDf
    
    def simulateDeltaWithTime(self, timeSteps):
        opt=copy.copy(self.option)
        spotPrice=copy.copy(opt.S0)
        mechanism=self.mechanism
        
        plotDf=pd.DataFrame(np.zeros([len(timeSteps), 3]), columns=['TimeToMaturity', 'DA_Delta', 'BLS_Delta'])
        plotDf['TimeToMaturity']=timeSteps
        
        def optPrice(assetPrice):
            opt.S0=assetPrice

            orders=self.traders.getOrders(opt, self.numOrders)
            orders=mechanism.clearOrders(orders)
       
            return mechanism.getPrice(orders)
        
        for i, p in enumerate(timeSteps):
            opt.T=p            
            plotDf.ix[i]['DA_Delta']=derivative(optPrice, x0=spotPrice, dx=20)
            
            opt.S0=spotPrice
            plotDf.ix[i]['BLS_Delta']=opt.delta()
            
            print i
     
        return plotDf
    
    
    def simulateGamma(self, assetPrices):
        opt=copy.copy(self.option)
        mechanism=self.mechanism
        
        plotDf=pd.DataFrame(np.zeros([len(assetPrices), 3]), columns=['AssetPrice', 'DA_Gamma', 'BLS_Gamma'])
        plotDf['AssetPrice']=assetPrices.values
        
        def optPrice(assetPrice):
            opt.S0=assetPrice
            orders=self.traders.getOrders(opt, self.numOrders)
            orders=mechanism.clearOrders(orders)
            
            return mechanism.getPrice(orders)
        
        for i, p in enumerate(assetPrices.values):
            plotDf.ix[i]['DA_Gamma']=derivative(optPrice, x0=p,dx=20, n=2)
            
            opt.S0=p            
            plotDf.ix[i]['BLS_Gamma']=opt.gamma()
            
            print plotDf.ix[i]['DA_Gamma'], plotDf.ix[i]['BLS_Gamma']
            
            print i
     
        return plotDf
    
    def simulateGammaWithTime(self, timeSteps):
        opt=copy.copy(self.option)
        spotPrice=copy.copy(opt.S0)
        mechanism=self.mechanism
        
        plotDf=pd.DataFrame(np.zeros([len(timeSteps), 3]), columns=['TimeToMaturity', 'DA_Gamma', 'BLS_Gamma'])
        plotDf['TimeToMaturity']=timeSteps
        
        def optPrice(assetPrice):
            opt.S0=assetPrice

            orders=self.traders.getOrders(opt, self.numOrders)
            orders=mechanism.clearOrders(orders)

            return mechanism.getPrice(orders)
        
        for i, p in enumerate(timeSteps):
            opt.T=p            
            plotDf.ix[i]['DA_Gamma']=derivative(optPrice, x0=spotPrice, dx=10, n=2)
            
            opt.S0=spotPrice
            plotDf.ix[i]['BLS_Gamma']=opt.gamma()
            
            print i
     
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