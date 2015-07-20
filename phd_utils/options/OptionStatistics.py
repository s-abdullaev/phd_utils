# -*- coding: utf-8 -*-
"""
Created on Sat Jul 11 00:50:01 2015

@author: Desmond
"""
import numpy as np
import pandas as pd
from pandas import DataFrame

class OptionStatistics(object):
    df=None
    
    def __init__(self, optionDf):
        self.df=optionDf
    
    def getOptionDelta(self):
        