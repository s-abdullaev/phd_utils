# -*- coding: utf-8 -*-
"""
Created on Sat Aug 22 05:00:22 2015

@author: Desmond
"""

from __future__ import division
from math import *
import numpy as np
import pandas as pd
import scipy.stats as stats
import scipy.optimize as optim
import copy
import vollib.black_scholes.implied_volatility as iv
import vollib.black_scholes as bls
import vollib.black_scholes.greeks.analytical as greeks

def critical(s, k1, k2, r, T, vol, callput):
    return optim.fsolve(corp1, s, args=(k1, k2, r, T, vol, callput))[0]

def corp1(ss, k1, k2, r, T, vol, callput):
    return k1-bls.black_scholes(callput, ss, k2, T, r, vol)


def cbnd(a,b,p):
    aa=[0.3253030, 0.4211071, 0.1334425, 0.006374323]    
    bb=[0.1337764, 0.6243247, 1.3425378, 2.2626645]
    sm=0
    if a<=0 and b<=0 and p<=0:
        inva=a/np.sqrt(2*(1-p**2))
        invb=b/np.sqrt(2*(1-p**2))
        sm=0
        for i, ai in enumerate(aa):
            for j, bj in enumerate(bb):
                sm=sm+aa[i]*aa[j]*np.exp(inva*(2*bb[i]-inva)+invb*(2*bb[j]-invb)+2*p*(bb[i]-inva)*(bb[j]-invb))
        sm=sm*np.sqrt(1-p**2)/np.pi
    elif a<=0 and b>=0 and p>=0:
        sm=stats.norm.cdf(a)-cbnd(a, -b, -p)
    elif a>=0 and b<=0 and p>=0:
        sm=stats.norm.cdf(b)-cbnd(-a, b, -p)
    elif a>=0 and b>=0 and p<=0:
        sm=stats.norm.cdf(a)+stats.norm.cdf(b)-1+cbnd(-a, -b, p)
    elif a*b*p>0:
        p1=(p*a-b)*np.sign(a)/np.sqrt(a**2-2*p*a*b+b**2)
        p2=(p*b-a)*np.sign(a)/np.sqrt(a**2-2*p*a*b+b**2)
        delta=(1-np.sign(a)*np.sign(b))/4
        sm=cbnd(a, 0, p1)+cbnd(b,0,p2)-delta
    return sm

def euroCompound(s, k1, k2, r, T1, T2, vol, cp):
    if cp==1 or cp==3:
        callput='c'
    elif cp==2 or cp==4:
        callput='p'
    sstar=critical(s, k1, k2, r, T2-T1, vol, callput)
    a1=(np.log(s/sstar)+(r+0.5*vol**2)*T1)/(vol*np.sqrt(T1))
    a2=a1-vol*np.sqrt(T1)
    b1=(np.log(s/k2)+(r+0.5*vol**2)*T2)/(vol*np.sqrt(T2))
    b2=b1-vol*np.sqrt(T2)
    Tratio=np.sqrt(T1/T2)
    if cp==1:
        return s*cbnd(a1,b1,Tratio)-k2*np.exp(-r*T2)*cbnd(a2,b2,Tratio)-np.exp(-r*T1)*k1*stats.norm.cdf(a2)
    elif cp==4:
        return s*cbnd(a1,-b1,-Tratio)-k2*np.exp(-r*T2)*cbnd(a2,-b2,-Tratio)+np.exp(-r*T1)*k1*stats.norm.cdf(a2)
    elif cp==2:
        return k2*np.exp(-r*T2)*cbnd(-a2,-b2,Tratio)-np.exp(-r*T1)*k1*stats.norm.cdf(-a2)-s*cbnd(-a1,-b1,Tratio)
    elif cp==3:
        return k2*np.exp(-r*T2)*cbnd(-a2,b2,-Tratio)+np.exp(-r*T1)*k1*stats.norm.cdf(-a2)-s*cbnd(-a1,b1,-Tratio)
        
