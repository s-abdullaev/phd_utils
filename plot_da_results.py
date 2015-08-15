# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 05:26:19 2015

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
from phd_utils.mechanisms.experiment import *
from phd_utils.tradingAlgos.DATrader import *
import scipy.optimize as optim
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns

def plotLin(filename, fields):
    df=pd.read_excel('results/da_experiments/mon_rnd_brwn/'+filename)
    df.plot(y=fields)

def plotHist(filename, fields):
    df=pd.read_excel('results/da_experiments/mon_rnd_brwn/'+filename)
    df.plot(fields, kind='hist')
