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
    def getOrders(self, optionType, size, **kwargs):
        assetPricingModel=kwargs['AssetPricingModel'] if 'AssetPricingModel' in kwargs else BrownianPricing(0.01, 0.05)
        optPricingModel=kwargs['OptionPricingModel'] if 'OptionPricingModel' in kwargs else MonteCarloPricing(assetPricingModel, 100)
        quantityModel=kwargs['QuantityModel'] if 'QuantityModel' in kwargs else RandomQuantity((-20,20))
        
        orders=pd.DataFrame(optPricingModel.getPrices(optionType, size))        
        orders=quantityModel.getQuantities(orders)
        orders.columns=['price', 'quantity']
        
        return orders

#opt=CallOption(S0=100,K=100,r=0.01,sigma=0.05, T=1)
#trader=DATrader()
#orders=trader.getOrders(opt, 100)
#print orders.head()
