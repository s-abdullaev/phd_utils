# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 02:29:18 2015

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
from phd_utils.mechanisms.online_models import *
from phd_utils.tradingAlgos.DATrader import *
import scipy.optimize as optim
import scipy.stats as stats
import matplotlib.pyplot as plt
import os

class DAExperiment(object):
    def __init__(self, folder, assetPrices, interestRates, traders, options, numTraders, linAssets, linTime):
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        self.folder=folder
        self.assetPrices=assetPrices
        self.interestRates=interestRates
        self.traders=traders
        self.atm_opt=copy.copy(options[0])
        self.otm_opt=copy.copy(options[1])
        self.itm_opt=copy.copy(options[2])
        self.linAssets=linAssets
        self.linTime=linTime
        self.numTraders=numTraders
        
    def start(self):
        print "%s - STARTING!!!" % self.folder
        print "%s - STARTING FOR ATM" % self.folder
        self.run(self.atm_opt, "atm")
        print "%s - STARTING FOR OTM" % self.folder        
        self.run(self.otm_opt, "otm")
        print "%s - STARTING FOR ITM" % self.folder
        self.run(self.itm_opt, "itm")
        print "%s - FINISHED" % self.folder
    
    def run(self, opt, name_prefix):
        da=DirectDASimulator(name_prefix, self.assetPrices, self.interestRates, self.traders, opt, self.numTraders)
        
        df=da.simulate()
        df.to_excel("%s/%s_%s.xls" % (self.folder, name_prefix, "Market"))
        #plotDf.plot(y=['BLSPrice', 'DAPrice'])
        
        df=da.simulateBSDelta(self.linAssets)
        df.to_excel("%s/%s_%s.xls" % (self.folder, name_prefix, "Delta"))
        
        df=da.simulateBSDeltaWithTime(self.linTime)
        df.to_excel("%s/%s_%s.xls" % (self.folder, name_prefix, "DeltaWithTime"))
        #plotDf.plot(x='TimeToMaturity', y=['DA_Delta', 'BLS_Delta'])
        
        df=da.simulateBSGamma(self.linAssets)
        df.to_excel("%s/%s_%s.xls" % (self.folder, name_prefix, "Gamma"))
        #plotDf.plot(x='AssetPrice', y=['DA_Gamma', 'BLS_Gamma'])
        
        df=da.simulateBSGammaWithTime(self.linTime)
        df.to_excel("%s/%s_%s.xls" % (self.folder, name_prefix, "GammaWithTime"))
        #plotDf.plot(x='TimeToMaturity', y=['DA_Gamma', 'BLS_Gamma'])
                
        df=da.simulateBSTheta(self.linAssets)
        df.to_excel("%s/%s_%s.xls" % (self.folder, name_prefix, "Theta"))
        #df.plot(x='AssetPrice', y=['DA_Theta', 'BLS_Theta'])
        
        df=da.simulateBSThetaWithTime(self.linTime)
        df.to_excel("%s/%s_%s.xls" % (self.folder, name_prefix, "ThetaWithTime"))
        #plotDf.plot(x='TimeToMaturity', y=['DA_Theta', 'BLS_Theta'])
        
        df=da.simulateVolCurve(self.linAssets)
        df.to_excel("%s/%s_%s.xls" % (self.folder, name_prefix, "VolCurve"))
        #plotDf.plot(x='Strikes', y='ImpVol')

class CDAExperiment(object):
    def __init__(self, folder, assetPrices, interestRates, traders, options):
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        self.folder=folder
        self.assetPrices=assetPrices
        self.interestRates=interestRates
        self.traders=traders
        self.atm_opt=copy.copy(options[0])
        self.otm_opt=copy.copy(options[1])
        self.itm_opt=copy.copy(options[2])
        
        
    def start(self):
        print "%s - STARTING!!!" % self.folder
        print "%s - STARTING FOR ATM" % self.folder
        self.run(self.atm_opt, "atm")
        for tr in self.traders: tr.proxyTradingModel.reset()
        print "%s - STARTING FOR OTM" % self.folder        
        self.run(self.otm_opt, "otm")
        for tr in self.traders: tr.proxyTradingModel.reset()
        print "%s - STARTING FOR ITM" % self.folder
        self.run(self.itm_opt, "itm")
        print "%s - FINISHED" % self.folder
    
    def run(self, opt, name_prefix):
        cda=OnlineDASimulator(name_prefix, self.assetPrices, self.interestRates, self.traders, opt)
        
        df, traderBidsDf, traderResultsDf=cda.simulate()
        df.to_excel("%s/%s_%s.xls" % (self.folder, name_prefix, "Market"))
        traderBidsDf.to_pickle("%s/%s_%s.xls" % (self.folder, name_prefix, "TraderOrders"))
        traderResultsDf.to_excel("%s/%s_%s.xls" % (self.folder, name_prefix, "TraderResults"))
