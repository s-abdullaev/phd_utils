# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 14:00:28 2015

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
from phd_utils.mechanisms.online_models import *
from phd_utils.mechanisms.experiment import *
from phd_utils.tradingAlgos.CDATrader import *
from phd_utils.options.EuropeanCompoundOption import *
import scipy.optimize as optim
import scipy.stats as stats
import matplotlib.pyplot as plt
import sys


price=5
option=CallOption(S0=100,K=105,r=0.05,sigma=0.2, T=0.5)
theta=0.07
phi_b=0.25
phi_a=1-phi_b
volume=5

@np.vectorize
def getLambdaAsk(p):
    return volume-(volume/price)*(p-price)

@np.vectorize    
def getLambdaBid(p):
    return volume+(volume/price)*(p-price)

@np.vectorize
def copelandObjective(p_a, p_b):
    puni=np.array([phi_b*(p_a-price), phi_a*(price-p_b)])
    pinf=np.array([max(euroCompound(option.S0, option.K, p_a, option.r, option.T-0.0001, option.T, option.sigma, 1),0), max(euroCompound(option.S0, option.K, p_b, option.r, option.T-0.0001, option.T, option.sigma, 3),0)])
    lambdas=np.array([getLambdaAsk(p_a), getLambdaBid(p_b)])
    obj=np.dot((1-theta)*puni-theta*pinf, lambdas)
    return obj
    

bids=np.linspace(0.01,price, 50)
asks=np.linspace(price,2*price, 50)
xx,yy=np.meshgrid(bids, asks, sparse=True)
z=copelandObjective(xx,yy)

plt.clf()
plt.imshow(z, extent=[0,price, price,2*price])
plt.show()