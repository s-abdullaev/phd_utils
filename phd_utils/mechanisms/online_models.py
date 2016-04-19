# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 02:21:08 2015

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
from orderbook import OrderBook
from orderbook.ordertree import OrderTree


class OnlineDA(object):
    def __init__(self):
        self.ob=OrderBook()
        self.day=0
        self.trades=[]
    
    def nextDay(self):
        self.day+=1
        self.trades=[]
        self.ob.asks=OrderTree()
        self.ob.bids=OrderTree()
    
    def submitOrder(self, order):
        trades, remOrder=self.ob.process_order(order, False, False)
        if len(trades)>0:
            self.trades.extend(trades)
        
        if not remOrder:
            order['isFilled']=True
            return trades, order
            
        if remOrder['quantity']<order['quantity']:
            order['isFilled']=True
            return trades, order
        
        order['isFilled']=False
        return trades, order
        
    def getOpenPrice(self):
        if len(self.trades)>0: 
            return self.trades[0]['price']
        return 0
    
    def getClosePrice(self):
        if len(self.trades)>0: 
            return self.trades[-1]['price']
        return 0
    
    def getHighPrice(self):
        if len(self.trades)>0: 
            return np.max([t['price'] for t in self.trades])
        return 0

    def getLowPrice(self):
        if len(self.trades)>0: 
            return np.min([t['price'] for t in self.trades])
        return 0
    
    def getVolume(self):
        return np.sum([t['quantity'] for t in self.trades])
    
class OnlineDASimulator():
    def __init__(self, name, assetPrices, interestRates, traders, option):
        self.name=name
        self.assetPrices=assetPrices
        self.interestRates=interestRates
        self.traders=traders
        self.option=option
        self.mechanism=OnlineDA()
    
    def simulate(self):
        opt=copy.copy(self.option)
        mechanism=self.mechanism
        traderCols=pd.MultiIndex.from_product([[tr.id for tr in self.traders], ['pHat', 'bid', 'ask', 'payoff', 'cash', 'options']], names=['trader_ids', 'trader_props'])
        
        cols=['CDAOpen', 'CDAHigh', 'CDALow', 'CDAClose', 'BLSPrice', 'Volume', 'AssetPrice', 'InterestRate']
        
        lastDay=opt.daysToMaturity()-1        
        
        
        tradersDf=pd.DataFrame(np.zeros([lastDay, len(self.traders)*6]), columns=traderCols)
        plotDf=pd.DataFrame(np.zeros([lastDay, 8]), columns=cols)
        plotDf['AssetPrice']=self.assetPrices.values[:-1]
        plotDf['InterestRate']=self.interestRates.values[:-1]
        
        for trader1 in self.traders:
            trader1.proxyTradingModel.ob=mechanism.ob
        
        steps=np.linspace(opt.T, 0, lastDay)
        for i, t, p, r in zip(range(lastDay), steps, self.assetPrices.values[:-1], self.interestRates.values[:-1]):
            opt.T=t
            opt.S0=p    
            opt.r=r
            
            plotDf.ix[i]['BLSPrice']=opt.blsPrice()
            plotDf.ix[i]['InterestRate']=opt.r            
            
            for trader1 in self.traders:
                trader1.updateOption(opt)
            
            shuffledIndice=np.random.permutation(len(self.traders))            
            for j in shuffledIndice:
                order=self.traders[j].getOrder()
                trades, order=mechanism.submitOrder(order)
                for trader2 in self.traders:
                    trader2.updateLastOrder(trades, order)
            
            for tr in self.traders:
                tradersDf.ix[i][tr.id]['pHat']=tr.proxyTradingModel.price
                tradersDf.ix[i][tr.id]['bid']=tr.proxyTradingModel.curBid
                tradersDf.ix[i][tr.id]['ask']=tr.proxyTradingModel.curAsk
                tradersDf.ix[i][tr.id]['payoff']=tr.proxyTradingModel.utility
                tradersDf.ix[i][tr.id]['cash']=tr.proxyTradingModel.cash
                tradersDf.ix[i][tr.id]['options']=tr.proxyTradingModel.options
            
            for h in range(10):
                print opt.blsPrice(), self.traders[h].proxyTradingModel.price, self.traders[h].proxyTradingModel.getAsk(), self.traders[h].proxyTradingModel.getBid(), self.traders[h].proxyTradingModel.cash, self.traders[h].proxyTradingModel.options
                        
            plotDf.ix[i]['CDAOpen']=mechanism.getOpenPrice()
            plotDf.ix[i]['CDAHigh']=mechanism.getHighPrice()
            plotDf.ix[i]['CDALow']=mechanism.getLowPrice()
            plotDf.ix[i]['CDAClose']=mechanism.getClosePrice()
            plotDf.ix[i]['Volume']=mechanism.getVolume()
            #print plotDf.ix[i]['CDAOpen'], plotDf.ix[i]['CDALow'], plotDf.ix[i]['CDAHigh'], plotDf.ix[i]['CDAClose'], plotDf.ix[i]['BLSPrice']
            
            mechanism.nextDay()
            print i
            
        traderResults=[[tr.id, (tr.proxyTradingModel.cash-tradersDf.ix[0][tr.id]['cash'])+float(tr.proxyTradingModel.options-tradersDf.ix[0][tr.id]['options'])*float(opt.payoff(opt.S0)), tr.proxyTradingModel.options-tradersDf.ix[0][tr.id]['option']] for tr in self.traders]
        traderResultsDf=pd.DataFrame(traderResults, columns=['trader_id', 'trader_cash', 'trader_options'])    
            
        
        return plotDf, tradersDf, traderResultsDf