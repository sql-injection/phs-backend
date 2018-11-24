# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 13:59:24 2017

@author: picku
"""

import numpy as np

def timeDomain(NN):

    L = float(len(NN))
    ANN = np.mean(NN)
    SDNN = np.std(NN)
    #SDSD = np.std(np.diff(NN))
    NN50 = len(np.where(abs(np.diff(NN)) > 50)[0])
    pNN50 = float(NN50)/L*100
    NN20 = len(np.where(abs(np.diff(NN)) > 20)[0])
    pNN20 = float(NN20)/L*100
    rMSSD = np.sqrt((1/L) * sum(np.diff(NN) ** 2))
    #MedianNN = np.median(NN)

    timeDomainFeats = [ANN,SDNN,pNN50,pNN20,rMSSD]

    return timeDomainFeats
