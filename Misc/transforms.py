# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 10:12:13 2017

@author: H131339
"""

import numpy as np
import scipy.signal as signal
 

# Function calculates the power spectral density of a signal
def psd(sig, fs):
    
    sigLen = sig.shape
    sigFFT = np.fft.fft(sig)
    sigFFT = sigFFT[0:int(sigLen[0]/2)]
    P = (1/sigLen[0] * np.abs(sigFFT))**2
    P[1:-2] = 2*P[1:-2]
    F = np.arange(0, fs/2, fs/sigLen[0])
    
    return(P, F)

# Function calculates the power spectral density of a signal similar to the Matlab native periodogram function
# Note: Result needs to be divided by signal length in seconds in order to conserve the amplitude of a sinusoidal signal
def periodogram(sig, fs):
    
    sigLen = sig.shape
    sigFFT = np.fft.fft(sig)
    sigFFT = sigFFT[0:int(sigLen[0]/2)]
    P = (1/(sigLen[0]*fs)) * np.abs(sigFFT)**2
    P[1:-2] = 2*P[1:-2]
    F = np.arange(0, fs/2, fs/sigLen[0])
    
    return(P,F)

    
# Function calculates the FFT of a signal according to the SEAFOM standard
def seafom_fft(sig, fs):

    # Detrend data
    sig = signal.detrend(sig)
    # Apply normalized Blackman-Harris window to data
    W = signal.blackmanharris(fs)
    normFact = fs/np.sum(W)
    sig = normFact * np.multiply(sig, W)
    # Calculate the FFT of the detrended and windowed data
    N = np.size(sig)
    sigFFT = np.fft.fft(sig)
    # Normalize the FFT output by number of samples
    sigFFT = sigFFT/N
    # Convert from double-sided to single-sided FFT and take absolute value
    sigFFT = np.abs(np.sqrt(2) * sigFFT[0:int(N/2)])
    # Correct for noise equivalent bandwidth of Blackman-Harris window
    neb = np.sqrt(np.size(W) * W.dot(W)/(np.sum(W)**2))
    sigFFT = sigFFT / neb
    F = np.arange(0, fs/2, fs/N)

    return(sigFFT, F)
