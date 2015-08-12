# -*- coding: utf-8 -*-
"""
Created on Sun Jul 19 23:09:01 2015

@author: Desmond
"""

from __future__ import division
import numpy as np
import pandas as pd
import copy
from phd_utils.options.EuropeanOption import *
from phd_utils.assetPricing.models import *
from phd_utils.optionPricing.qntyModels import *
from phd_utils.optionPricing.models import *
import scipy.optimize as optim
import scipy.stats as stats
import matplotlib.pyplot as plt

class DATrader(object):
    def __init__(self, **kwargs):
        self.assetPricingModel=kwargs['AssetPricingModel'] if 'AssetPricingModel' in kwargs else BrownianPricing(0.01, 0.05)
        self.optPricingModel=kwargs['OptionPricingModel'] if 'OptionPricingModel' in kwargs else MonteCarloPricing(self.assetPricingModel, 100)
        self.quantityModel=kwargs['QuantityModel'] if 'QuantityModel' in kwargs else RandomQuantity((-20,20))
    
    def getOrders(self, optionType, size, **kwargs):
        orders=pd.DataFrame(self.optPricingModel.getPrices(optionType, size))        
        orders=self.quantityModel.getQuantities(orders)
        orders.columns=['price', 'quantity']
        
        return orders

#opt=CallOption(S0=100,K=100,r=0.01,sigma=0.05, T=1)
#trader=DATrader()
#orders=trader.getOrders(opt, 100)
#print orders.head()

class DATraderCollection(object):
    def __init__(self, traderCol, proportions):
        self.traders=traderCol
        self.props=proportions
    
    def getOrders(self, optionType, size):
        orders=pd.DataFrame(data=None, columns=['price', 'quantity'])
        for trader, perc in zip(self.traders, self.props):
            orders=orders.append(trader.getOrders(optionType, int(size*perc)))
        orders=orders.reset_index()
        
        return orders