# -*- coding: utf-8 -*-
"""
Created on Sat Jul 18 04:31:53 2015

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

class RandomQuantity(object):
    def __init__(self, qntyRange):
        self.qntyRange=qntyRange
    
    def getQuantities(self, optionPrices, opt):
        size=len(optionPrices)
        optionPrices['quantities']=optionPrices['isLong']*np.random.randint(0, self.qntyRange[1], size)
        return optionPrices

class RandomSingularQuantity(object):
    
    def getQuantities(self, optionPrices, opt):
        optionPrices['quantities']=optionPrices['isLong']
        return optionPrices


class LinearQuantity(object):
    def __init__(self, equib_quant):
        self.equib_quant=equib_quant
    
    def getQuantities(self, optionPrices, opt):
        def demFunc(x):
            if opt.blsPrice()>0:
                val=abs(x)*self.equib_quant/opt.blsPrice()
            else:
                val=0
            return val
        
        def supFunc(x):
            if opt.blsPrice()>0:
                val=2*self.equib_quant-(self.equib_quant/opt.blsPrice())*abs(x)
            else:
                val=2*self.equib_quant
            
            return -np.round(val)
        
        optionPrices['quantities']=[demFunc(row['prices']) if row['isLong']==1 else supFunc(row['prices']) for i, row in optionPrices.iterrows()]
        return optionPrices

class OptionPortfolioQuantity(object):
    def __init__(self, qntyRange):
        self.qntyRange=qntyRange
        
    def getQuantities(self, optionChain):
        pSize=len(OPTION_PORTFOLIOS)
        oSize=len(optionChain)
        scalers=np.random.randint(qntyRange[0], qntyRange[1], size=oSize)        
        
        idxes=np.random.randint(0, pSize, size=oSize)
        df=pd.DataFrame(OPTION_PORTFOLIOS.ix[idxes])
        
        df=df.multiply(scalers, axis=0)
        df.index.name='StratName'
        df=df.reset_index()
        
        return optionChain.join(df)
        
        