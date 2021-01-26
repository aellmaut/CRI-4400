# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 14:06:56 2017

@author: H131339
"""

import numpy as np

def getWeightedPhaseData(I, Q, channel):

    # Laser 1
    phaseData = getPhaseData(I[0][:,channel], Q[0][:, channel])
    phaseData = np.hstack([phaseData[0], np.diff(phaseData)])
    qualityFact = (I[0][:,channel]*I[0][:,channel] +Q[0][:,channel]*Q[0][:,channel]) + 0.0001
    weightedPhaseData = qualityFact*phaseData
    qualityFactAccum = qualityFact
    
    for i in range(1, len(I)):
        # Laser i
        phaseData = getPhaseData(I[i][:,channel], Q[i][:, channel])
        phaseData = np.hstack([phaseData[0], np.diff(phaseData)])
        qualityFact = (I[i][:,channel]*I[i][:,channel] +Q[i][:,channel]*Q[i][:,channel]) + 0.0001
        weightedPhaseData = weightedPhaseData + qualityFact*phaseData
        qualityFactAccum = qualityFactAccum + qualityFact
    
    # Normalize weighted stack
    weightedPhaseData = weightedPhaseData/qualityFactAccum
    weightedPhaseData = np.cumsum(weightedPhaseData)
    
    return(weightedPhaseData)


def getPhaseData(I,Q):
    
    phaseData = np.unwrap(np.arctan2(Q,I))
    
    return(phaseData)

# Function converts from phase in radians to pico strain
def phaseToStrain(phaseData, refractiveIndex, ITUchannel, gaugeLength):
    # Constants
    xi = 0.78 # Photo-Elastic scaling factor
    # ITU Channel to Wavelength in nm dictionary
    ITUchann2wavelength = { 35: 1549.32,
                        36: 1548.51,
                        37: 1547.72,
                        38: 1546.92,
                        39: 1546.12,
                        40: 1545.32,
                        41: 1544.53,
                        42: 1543.73,
                        43: 1542.94,
                        44: 1542.14,
                        45: 1541.35,
                        46: 1540.56,
                        47: 1539.77}

    strainData = (ITUchann2wavelength[ITUchannel]/(4*np.pi*refractiveIndex*gaugeLength * xi)) * phaseData * 10**3 # 10**3 factor is to convert from nano to pico

    return(strainData)