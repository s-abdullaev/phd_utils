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
    
    def getQuantities(self, optionPrices):
        size=len(optionPrices)
        optionPrices['quantities']=np.random.randint(self.qntyRange[0], self.qntyRange[1], size)
        return optionPrices

class LinearQuantity(object):
    def __init__(self, linParams):
        self.linParams=linParams
    
    def getQuantities(self, optionPrices):
        def demFunc(x):
            return np.round(np.max(self.linParams[0]*abs(x)+self.linParams[1], 0))
        
        def supFunc(x):
            return -np.round(abs(self.linParams[2]*abs(x)+self.linParams[3]))
        
        optionPrices['quantities']=optionPrices['prices'].apply(lambda x: demFunc(x) if np.random.rand()>0.5 else supFunc(x))
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
        
        