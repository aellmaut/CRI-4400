# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 14:27:17 2017

@author: H131339
"""
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sp
import math
import pdb

import transforms
import IQtoPhase
import dataAcq


##################################################################################
# AMPLIFIER SETUP
##################################################################################
def amplifierSetup(gui, interrogator):
    gui.textWindow.insert(tk.END, 'Starting Amplifier Setup for DAS interrogator ' + interrogator.name + '\n')
    gui.textWindow.see(tk.END)
    gui.progressBar.step(0.1)
    gui.progressBar.update()
    # Set dither to sine wave with amplitude of 2V and frequency of 10 Hz
    interrogator.enableDither(2, 10)
    # Set DAS sampling frequency to 1.6 kHz
    if gui.InterrogatorHandle.fs != 1600:
        gui.textWindow.insert(tk.END, 'Setting DAS sampling frequency to 1.6 kHz ...')
        gui.textWindow.see(tk.END)
        gui.InterrogatorHandle.setFs(1600)
        gui.popupMenu_fsDAS.current(0)
        gui.progressBar["value"] = 0.2
        gui.progressBar.update()
        gui.textWindow.insert(tk.END, ' done\n')
        gui.textWindow.see(tk.END)
    
    # Initialize receive- and launch EDFAs
    gui.textWindow.insert(tk.END, 'Initializing launch EDFA ... ')
    gui.textWindow.see(tk.END)
    [launchEDFAcurr, recEDFAcurr] = initEDFAs(gui, interrogator)
    gui.textWindow.insert(tk.END, 'success (' + str(launchEDFAcurr) + 'mA)\n')
    gui.textWindow.see(tk.END)
    gui.progressBar.step(0.1)
    gui.progressBar.update()
    
    # Determine sensing fiber regions at 1.6 kHz
    gui.textWindow.insert(tk.END, 'Detecting sensing fiber regions ... ')
    gui.textWindow.see(tk.END)
    gui.fiberSensingRegions = detectSensingFiberRegions(gui, interrogator)
    gui.textWindow.insert(tk.END, 'success\n')
    for i in range(0, len(gui.fiberSensingRegions)):
        gui.textWindow.insert(tk.END, 'Fiber Region ' + str(i+1) + ': ' + str(gui.fiberSensingRegions[i][0]) + '-' + str(gui.fiberSensingRegions[i][1]) + '\n')
        print('Fiber Sensing Region ' + str(i+1) + ': ' + str(gui.fiberSensingRegions[i][0]) + '-' + str(gui.fiberSensingRegions[i][1]))     
    gui.textWindow.see(tk.END)
    gui.progressBar.step(0.1)
    gui.progressBar.update()
     
    # Optimize DAS sampling frequency
    fsDAS = optimizeDASfs(gui)
    if fsDAS != gui.InterrogatorHandle.fs:
 
        # Change DAS sampling frequency
        gui.InterrogatorHandle.setFs(fsDAS)
        ind = [x for x in range(len(gui.InterrogatorHandle.dict_ts2fs)) if gui.InterrogatorHandle.dict_ts2fs[x][1] == fsDAS]
        gui.popupMenu_fsDAS.current(ind)
         
        # Re-determine sensing fiber region for optimized DAS sampling frequency
        gui.textWindow.insert(tk.END, 'Detecting sensing fiber regions  ... ')
        gui.textWindow.see(tk.END)
        #pdb.set_trace()
        gui.fiberSensingRegions = detectSensingFiberRegions(gui, interrogator)
        gui.textWindow.insert(tk.END, 'success\n')
 
        for i in range(0, len(gui.fiberSensingRegions)):
            gui.textWindow.insert(tk.END, 'Fiber Region ' + str(i+1) + ': ' + str(gui.fiberSensingRegions[i][0]) + '-' + str(gui.fiberSensingRegions[i][1]) + '\n')
            print('Fiber Sensing Region ' + str(i+1) + ': ' + str(gui.fiberSensingRegions[i][0]) + '-' + str(gui.fiberSensingRegions[i][1]))
             
        gui.textWindow.see(tk.END)
        gui.progressBar.step(0.1)
        gui.progressBar.update()
 
    # Set R-EDFA to default value based on pulse width
    if gui.InterrogatorHandle.pulseWidth <= 20:
        recEDFAcurr = 100
    elif gui.InterrogatorHandle.pulseWidth <= 70:
        recEDFAcurr = 95
    elif gui.InterrogatorHandle.pulseWidth <= 100:
        recEDFAcurr = 92
    interrogator.setRecEDFA(recEDFAcurr)
 
    # Determine optimal launch EDFA amplifier setting
    gui.textWindow.insert(tk.END, 'Optimizing launch EDFA current ... ')
    gui.textWindow.see(tk.END)
    launchEDFAcurr = launchAmplifierSetup(gui, interrogator, launchEDFAcurr, gui.fiberSensingRegions[0][0], gui.fiberSensingRegions[-1][1])
    interrogator.setLaunchEDFA(launchEDFAcurr)
    gui.selectedLaunchEDFA.set(launchEDFAcurr)
    gui.textWindow.insert(tk.END, 'success (' + str(launchEDFAcurr) + ' mA)\n')
    gui.textWindow.see(tk.END)
 
    # Determine optimal receive EDFA amplifier setting
    gui.progressBar.step(0.1)
    gui.update()
    gui.textWindow.insert(tk.END, 'Optimizing receive EDFA current ... ')
    gui.textWindow.see(tk.END)
    recEDFAcurr = receiveAmplifierSetup(gui, interrogator, gui.fiberSensingRegions[0][0], gui.fiberSensingRegions[0][1])
    interrogator.setRecEDFA(recEDFAcurr)
    gui.selectedRecEDFA.set(recEDFAcurr)
    gui.textWindow.insert(tk.END, 'success (' + str(recEDFAcurr) + ' mA)\n')
    gui.textWindow.see(tk.END)
     
    # Create Oscilloscope plots displaying optical backscattered energy after amplifier setup
    gui.progressBar.step(0.1)
    gui.update()
    gui.textWindow.insert(tk.END, 'Generating Oscilloscope Plots ... ')
    gui.textWindow.see(tk.END)
    generateOscilloscopePlot(gui, interrogator, 1, gui.fiberSensingRegions[0][0], gui.fiberSensingRegions[-1][1]) # Laser 1
    generateOscilloscopePlot(gui, interrogator, 2, gui.fiberSensingRegions[0][0], gui.fiberSensingRegions[-1][1]) # Laser 2
    gui.textWindow.insert(tk.END, 'success\n')
    gui.textWindow.see(tk.END)
     
    # Disable dither
    interrogator.disableDither()
    
    

# Function determines the minimum launch-side EDFA current which results in a detectable optical backscatter signal
def initEDFAs(gui, interrogator):
    
    # Recording parameters
    laserNum = 3 # 1 = laser 1; 2 = laser 2; 3 = laser 1 & 2
    recLen = 0.1 # Record length in seconds for which backscatter energy will be calculated per iteration
    firstChann = 65 # First channel for backscatter energy calculation
    lastChann = 96 # Last channel for backscatter energy calculation  
    launchEDFAcurr = 100 # Launch EDFA current
    recEDFAcurr = 200 # Receive EDFA current
    # Initialize EDFAs
    interrogator.setLaunchEDFA(launchEDFAcurr)
    interrogator.setRecEDFA(recEDFAcurr)
    
    # Iteratively increase launch EDFA until difference in backscatter energy between two iterations is higher than the pre-defined threshold
    success = 0
    i = 1
    while success == 0:
        # Increase launch EDFA by 10 mA
        launchEDFAcurr = launchEDFAcurr + 10
        interrogator.setLaunchEDFA(launchEDFAcurr)
        # Acquire data
        [data, firstChann, lastChann] = dataAcq.getData(gui, firstChann, lastChann, recLen, laserNum)      
        # Extract I/Q data from data buffer
        # If both lasers are used for calibration, the maximum I and Q value of the two lasers is used
        if laserNum == 3:
            # Take maximum I/Q value 
            I = np.maximum(data[interrogator.boardNum][:, 0:-4:4], data[interrogator.boardNum][:,2:-2:4])
            Q = np.maximum(data[interrogator.boardNum][:, 1:-3:4], data[interrogator.boardNum][:,3:-1:4])
        else:
            I = data[interrogator.boardNum][:,0:-2:2]
            Q = data[interrogator.boardNum][:,1:-1:2]
        # Calculate the median I/Q radius over time for each channel
        IQrad = np.median(np.sqrt(I*I+Q*Q), axis=0)
        # Calculate the rms value over the median I/Q radii
        IQrad_rms = np.sqrt(np.mean(IQrad**2))
        print(IQrad_rms)
        # Execution of while loop stops if new IQ radius value exceeds old IQ radius value by more than defined in 'thresh_EDFAinit'
        if i == 1:
            IQrad_rms_old = IQrad_rms
            
        if (IQrad_rms - IQrad_rms_old) > gui.thresh_EDFAinit:
             success = 1
        
        i += 1
        IQrad_rms_old = IQrad_rms
        
    return (launchEDFAcurr, recEDFAcurr)

# Function computes the optimal launch EDFA current 
def launchAmplifierSetup(gui, interrogator, launchEDFAcurr, firstChann, lastChann):
    
    # Recording parameters
    laserNum = 3 # 1 = laser 1; 2 = laser 2; 3 = laser 1 & 2
    recLen = 0.1 # Record length in seconds per data acquisition run
    currentStepSize = 10 # Increase in launch amplifier current per iteration
    
    # Iteratively increase launch EDFA current until backscatter energy over last 200 channels decays
    success = 0
    IQrad_arr = []
    launchEDFAcurr_arr = []
    while success == 0:       
        # Acquire data
        [data, firstChann, lastChann] = dataAcq.getData(gui, firstChann, lastChann, recLen, laserNum)
        # Extract I/Q data from data buffer
        # If both lasers are used for calibration, the maximum I and Q value of the two lasers is used
        if laserNum == 3:
            # Take maximum I/Q value 
            I = np.maximum(data[interrogator.boardNum][:, 0:-4:4], data[interrogator.boardNum][:,2:-2:4])
            Q = np.maximum(data[interrogator.boardNum][:, 1:-3:4], data[interrogator.boardNum][:,3:-1:4])
        else:
            I = data[interrogator.boardNum][:,0:-2:2]
            Q = data[interrogator.boardNum][:,1:-1:2]
        # Calculate the median I/Q radius over time for each channel
        IQrad = np.median(np.sqrt(I*I+Q*Q), axis=0)
        # Calculate the rms value over last 200 channels
        IQrad_arr.append(np.sqrt(np.mean(IQrad[-200:-1]**2)))
        launchEDFAcurr_arr.append(launchEDFAcurr)
        gui.progressBar.step(0.005)
        gui.update()
        print('Optical Backscatter Energy: ' + str(IQrad_arr[-1]))
        # Exit while loop if IQ radius rms value over last 200 channls is below the rms value of 15 iterations earlier
        if (len(IQrad_arr) > 15 and IQrad_arr[-1] < IQrad_arr[-16]) or launchEDFAcurr == 1300:
            success = 1
            plt.plot(launchEDFAcurr_arr, IQrad_arr, 'x-')
            ind = IQrad_arr.index(max(IQrad_arr))
            optLaunchEDFAcurr, = plt.plot(launchEDFAcurr_arr[ind], IQrad_arr[ind], '-o', ms=12, lw=2, alpha=0.7, mfc='orange', label = 'Optimal Launch EDFA Current: ' + str(launchEDFAcurr_arr[ind]) + ' mA')
            plt.legend(handles=[optLaunchEDFAcurr])
            plt.title(interrogator.name + ' Launch Amplifier Setup Result: GL ' + str(interrogator.gaugeLength) + 'm', fontweight= 'bold')
            plt.xlabel('Launch EDFA Current (mA)')
            plt.ylabel('Optical Backscatter Energy')
            plt.grid(True)
            gui.calibResultsPdf.savefig()
            plt.close()
        else:
            # Increase launch EDFA current
            launchEDFAcurr += currentStepSize
            interrogator.setLaunchEDFA(launchEDFAcurr)
        
    return(launchEDFAcurr_arr[ind])
        
# Function calculates ideal receive EDFA current
def receiveAmplifierSetup(gui, interrogator, firstChann, lastChann):
    
    # Recording parameters
    laserNum = 3 # 1 = laser 1; 2 = laser 2; 3 = laser 1 & 2
    recLen = 0.1 # Record length in seconds per data acquisition run    
    updateStepSize = 20 # Learning rate of R-EDFA
    
    # Iteratively decrease receive EDFA current until number of saturated channels is below the pre-defined threshold
    success = 0
    saturatedChannRatio_arr = []
    recEDFAcurr_arr = []
    recEDFAcurr_arr.append(200)
    while success == 0:
        # Update progress bar
        gui.progressBar.step(0.005)
        gui.update()
        # Set receive EDFA to updated current value
        interrogator.setRecEDFA(recEDFAcurr_arr[-1])
        # Acquire data
        [data, firstChann, lastChann] = dataAcq.getData(gui, firstChann, lastChann, recLen, laserNum)
        # Extract I/Q data from data buffer
        # If both lasers are used for calibration, the maximum I and Q value of the two lasers is used
        if laserNum == 3:
            # Take maximum I/Q value 
            I = np.maximum(data[interrogator.boardNum][:, 0:-4:4], data[interrogator.boardNum][:,2:-2:4])
            Q = np.maximum(data[interrogator.boardNum][:, 1:-3:4], data[interrogator.boardNum][:,3:-1:4])
        else:
            I = data[interrogator.boardNum][:,0:-2:2]
            Q = data[interrogator.boardNum][:,1:-1:2]
        # Reduce receive EDFA current if number of saturated channels exceeds threshold
        saturatedChannRatio_arr.append(getSaturatedChannRatio(I,Q))
        print('Channel Saturation Ratio: ' + str(saturatedChannRatio_arr[-1]))
        if saturatedChannRatio_arr[-1] < gui.thresh_saturatedChannRatio:
            success = 1
        else:
            # Update receiver EDFA current in mA
            recEDFAcurr_arr.append(recEDFAcurr_arr[-1] - max(1, math.floor(updateStepSize*saturatedChannRatio_arr[-1])))
    
    saturatedChannRatioPer = [i * 100 for i in saturatedChannRatio_arr]   
    plt.plot(recEDFAcurr_arr, saturatedChannRatioPer, 'x-')
    plt.plot(np.array([recEDFAcurr_arr[0]+10, recEDFAcurr_arr[-1]-10]), np.array([gui.thresh_saturatedChannRatio * 100, gui.thresh_saturatedChannRatio * 100]), 'r--')
    recEDFAcurr_plt, = plt.plot(recEDFAcurr_arr[-1], saturatedChannRatioPer[-1], '-o', 
                                ms=12, lw=2, alpha=0.7, mfc='orange', label = 'Optimal Receive EDFA Current: ' + str(recEDFAcurr_arr[-1]) + ' mA')
    plt.legend(handles=[recEDFAcurr_plt])
    plt.xlim(recEDFAcurr_arr[-1]-10, recEDFAcurr_arr[0]+10)
    plt.gca().invert_xaxis()
    plt.gca().text(recEDFAcurr_arr[0], (gui.thresh_saturatedChannRatio * 100) + 2.5, 'Saturation Threshold: ' + str(gui.thresh_saturatedChannRatio * 100) + '%',
            verticalalignment='bottom', horizontalalignment='left', color='red', fontweight='bold')
    plt.title(interrogator.name + ' Receive Amplifier Setup Result: GL ' + str(interrogator.gaugeLength) + 'm', fontweight= 'bold')
    plt.xlabel('Receive EDFA Current (mA)')
    plt.ylabel('Saturated Channel Ratio (%)')
    plt.grid(True)
    gui.calibResultsPdf.savefig()
    plt.close()
        
    return(recEDFAcurr_arr[-1])
        
def getSaturatedChannRatio(I,Q):
    
    thresh = 0.82 # I/Q Radius Threshold for saturation detection
    stepSize = 500
    saturatedChannRatio = 0
    
    IQmax = np.maximum(np.abs(I), np.abs(Q))
    IQmax = np.amax(IQmax, axis=0)
    
    for i in range(0, math.ceil(IQmax.size/stepSize)):
        
        IQmax_small = IQmax[i*stepSize:min((i+1)*stepSize, IQmax.size)]
        saturatedChanns = np.size(np.nonzero(IQmax_small > thresh))
        saturatedChannRatio = max(saturatedChannRatio, saturatedChanns/IQmax_small.size)
        
    return(saturatedChannRatio)
        
        
        
##################################################################################
# FIBER END DETECTION
##################################################################################
def fiberEndDetection(gui):
    
    gui.textWindow.insert(tk.END, '\nStarting Fiber End Detection\n')
    gui.textWindow.see(tk.END)
    gui.progressBar.step(0.1)
    gui.progressBar.update()
      
    # Fine fiber end detection
    gui.textWindow.insert(tk.END, 'Searching for fiber end ... ')
    gui.textWindow.see(tk.END)
    firstChann = max(1, gui.fiberSensingRegions[-1][1] - 100)
    ind = [x for x in range(len(gui.InterrogatorHandle.dict_ts2fs)) if gui.InterrogatorHandle.dict_ts2fs[x][1] == gui.InterrogatorHandle.fs]
    lastChann = min(gui.InterrogatorHandle.dict_ts2fs[ind[0]][0] + 50, gui.fiberSensingRegions[-1][1] + 100)
    #lastChann = min(1/gui.InterrogatorHandle.fs * 10**8, gui.fiberSensingRegions[-1][1] + 100)

    gui.fiberEndChann = detectFiberEnd_fine(gui, firstChann, lastChann)
    if gui.fiberEndChann != 0:
        gui.textWindow.insert(tk.END, 'success (' + str(gui.fiberEndChann) + ')\n')
    else:
        gui.textWindow.insert(tk.END, ' failed\n')
        gui.fiberEndChann = gui.fiberSensingRegions[-1][1]

    gui.textWindow.see(tk.END)
    gui.progressBar.step(0.1)
    gui.progressBar.update()
    
    # Flag fiber end detection setup as having completed successfully
    gui.isCalibrated[1] = 1


def detectSensingFiberRegions(gui, interrogator):

    # Recording parameters
    laserNum = 3 # 1 = laser 1; 2 = laser 2; 3 = laser 1 & 2
    firstChann = 1
    ind = [x for x in range(len(gui.InterrogatorHandle.dict_ts2fs)) if gui.InterrogatorHandle.dict_ts2fs[x][1] == gui.InterrogatorHandle.fs]
    lastChann = gui.InterrogatorHandle.dict_ts2fs[ind[0]][0] + 50 # Last channel is set to maximum permissible value for current DAS sampling frequency plus 50. This ensure that at least 50 channels at the end do not show any optical activity.
    recLen = 0.1 # Record length in seconds
    fiberSensingRegion = []
    fiberSensingRegionClean = []
    
    # Acquire data
    [data, firstChann, lastChann] = dataAcq.getData(gui, firstChann, lastChann, recLen, laserNum)
    # Extract I/Q data from data buffer
    # If both lasers are used for calibration, the maximum I and Q value of the two lasers is used
    if laserNum == 3:
        # Take maximum I/Q value 
        I = np.maximum(data[interrogator.boardNum][:, 0:-4:4], data[interrogator.boardNum][:,2:-2:4])
        Q = np.maximum(data[interrogator.boardNum][:, 1:-3:4], data[interrogator.boardNum][:,3:-1:4])
    else:
        I = data[interrogator.boardNum][:,0:-2:2]
        Q = data[interrogator.boardNum][:,1:-1:2]
    # Calculate the median I/Q radius over time for each channel
    IQrad = np.median(np.sqrt(I*I+Q*Q), axis=0) 

    # Remove DC component from I/Q radius
    IQrad = IQrad - np.mean(IQrad[0:10])

    # Get threshold for fiber sensing region detection
    thresh_optActivity = 5*np.max(np.abs(IQrad[(lastChann-50):]))
    print('Threshold for fiber sensing region detection: ' + str(thresh_optActivity))

    # Find all fiber sensing regions
    startFound = 0
    startChann = 0
    for i in range(0, lastChann-1):
        # Find individual fiber sensing regions
        if startFound == 0 and IQrad[i] > thresh_optActivity:
            startFound = 1
            startChann = i
        elif startFound == 1 and IQrad[i] < thresh_optActivity:
            startFound = 0
            fiberSensingRegion.append([startChann, i-1])

    # Clean fiber sensing regions
    while len(fiberSensingRegion) != 0:
        
        if len(fiberSensingRegion) == 1 or (fiberSensingRegion[1][0] - fiberSensingRegion[0][1]) > gui.thresh_sensingRegionGap:
            fiberSensingRegionClean.append(fiberSensingRegion[0])           
        else:
            fiberSensingRegion[1][0] = fiberSensingRegion[0][0]

        fiberSensingRegion.remove(fiberSensingRegion[0])

    # Plot results
    plt.plot(IQrad)
    for i in range(0,len(fiberSensingRegionClean)):
        plt.plot(np.array([fiberSensingRegionClean[i][0], fiberSensingRegionClean[i][0]]), np.array([0, 0.2]), 'r--')
        plt.plot(np.array([fiberSensingRegionClean[i][1], fiberSensingRegionClean[i][1]]), np.array([0, 0.2]), 'r--')
    
    plt.ylabel('I/Q Radius')
    plt.xlabel('Channel')
    plt.ylim(0, 1.4)
    plt.grid(True)
    plt.suptitle('Oscilloscope Plot - Laser ' + str(laserNum) + ': GL ' + str(interrogator.gaugeLength) + 'm @ ' + str(gui.InterrogatorHandle.fs) + 'Hz', fontweight= 'bold')
    plt.show()

    return(fiberSensingRegionClean)
    

def detectFiberEnd_fine(gui, firstChann, lastChann):
    
    # Recording parameters
    laserNum = 3
    recLen = 5 # Record length in seconds
    # Sensitivity of fiber stretchers given as rad per V
    if len(gui.InterrogatorHandle.interrogators) == 1: # External Fiber Stretcher Module
        radPerV = 1.3 
    else: # WDM
        radPerV = 0.8

    thresh = 0.75 # Treshold for fiber end detection
    fiberEndChann = 0 # Variable holding found fiber end channel
    
    # Set dither to 10 Hz sine wave with amplitude of 2V
    ditherAmp = 2
    ditherFreq = 10
    for interrogator in gui.InterrogatorHandle.interrogators:
        interrogator.enableDither(ditherAmp, ditherFreq)
    
    # Acquire data
    [data, firstChann, lastChann] = dataAcq.getData(gui, firstChann, lastChann, recLen, laserNum)

    # Extract I/Q data from data buffer for each laser
    I = []
    Q = []
    for i in range(len(data)):
        I.append(data[i][:, 0:-4:4])
        I.append(data[i][:, 2:-2:4])
        Q.append(data[i][:, 1:-3:4])
        Q.append(data[i][:, 3:-1:4])
    
    dataSize = I[0].shape     
    sigPow10Hz = np.zeros(dataSize[1])

    # Extract signal energy at dither signal frequency
    for i in range(dataSize[1]):
        # Get weighted phase data
        weightedPhaseData = IQtoPhase.getWeightedPhaseData(I,Q,i)
        # Calculate fft and extract signal energy at 10 Hz
        [P,F] = transforms.psd(weightedPhaseData, gui.InterrogatorHandle.fs)
        ind = np.nonzero(F == ditherFreq)
        sigPow10Hz[i] = P[ind]
    
    # Convert signal power at 10 Hz to amplitude
    sigAmp10Hz = np.sqrt(sigPow10Hz*2) / radPerV
    # Remove outliers
    sigAmp10Hz = sp.medfilt(sigAmp10Hz, 3)
    
    plt.plot(np.arange(firstChann, lastChann), sigAmp10Hz)
    plt.show()

    # Compute fiber end location
    n = 0
    fiberEndFound = 0
    while n < sigAmp10Hz.size-5 and fiberEndFound == 0:
        if np.sum(sigAmp10Hz[n:n+5] < (ditherAmp*thresh)) == 5:
            fiberEndFound = 1
            # Subtract pulse width from detected fiber end channel
            fiberEndChann = firstChann + n - gui.InterrogatorHandle.pulseWidth/10 - 1
            print('Fiber End Channel: ' + str(int(fiberEndChann)))
            plt.plot(np.arange(firstChann, lastChann), sigAmp10Hz)
            fiberEnd_plt, = plt.plot(np.array([fiberEndChann + gui.InterrogatorHandle.pulseWidth/10, fiberEndChann + gui.InterrogatorHandle.pulseWidth/10]), np.array([0, ditherAmp + 0.5]), 'r--', label='Fiber End Channel: ' + str(int(fiberEndChann)))
            plt.legend(handles=[fiberEnd_plt])
            plt.title('Fiber End Detection Result: GL ' + str(gui.InterrogatorHandle.interrogators[gui.popupMenu_DASinterrogator.current()].gaugeLength) + 'm', fontweight= 'bold')
            plt.xlim(firstChann, lastChann)
            plt.ylim(0, ditherAmp + 1)
            plt.xlabel('DAS Channel')
            plt.ylabel('Dither Signal Amplitude (V)')
            plt.grid(True)
            gui.calibResultsPdf.savefig()
            
        else:
            n = n + 1
    
    


    # Disable dither
    for interrogator in gui.InterrogatorHandle.interrogators:
        interrogator.disableDither()
    
    return(int(fiberEndChann))
    
  
##################################################################################
# I/Q IMBALANCE CORRECTION
################################################################################## 
def IQImbalanceCorrection(gui):
    
    # Recording parameters
    recLen = 1 # Record length in seconds
    precision = 2 # Precision of IQ compensation parameters (e.g. precision of 2 implies that IQ imbalance correction parameter will be rounded to its closest number with two decimal places)
   
    gui.textWindow.insert(tk.END, '\nStarting I/Q Imbalance Correction for DAS interrogator ' + gui.InterrogatorHandle.interrogators[gui.popupMenu_DASinterrogator.current()].name + '\n')
    gui.textWindow.see(tk.END)
    gui.progressBar.step(0.1)
    gui.progressBar.update()
    
     # Set dither to 10 Hz sine wave with amplitude of 2.5V
    ditherAmp = 2.5
    ditherFreq = 10
    gui.InterrogatorHandle.interrogators[gui.popupMenu_clockMode.current()].enableDither(ditherAmp, ditherFreq)
    
    for i in range(0,2):
        # Acquire data
        [data, firstChann, lastChann] = dataAcq.getData(gui, gui.fiberSensingRegions[0][0], gui.fiberSensingRegions[-1][1], recLen, i+1)
        
        # Extract I/Q data from data buffer for each laser
        I = data[:, 0:-2:2]
        Q = data[:, 1:-1:2]
        # Initialize arrays holding I/Q Imbalance Correction parameters per channel
        if i == 0:
            IQgainArr = np.zeros((lastChann-firstChann, 2))
            IoffsetArr = np.zeros((lastChann-firstChann, 2))
            QoffsetArr = np.zeros((lastChann-firstChann, 2))
        
        for j in range(0, IQgainArr.shape[0]):
            # Downsample I/Q data to 1kHz
            Idown = sp.decimate(I[:,j], int(gui.InterrogatorHandle.interrogators[gui.popupMenu_clockMode.current()].fs/1000), zero_phase=True)
            Qdown = sp.decimate(Q[:,j], int(gui.InterrogatorHandle.interrogators[gui.popupMenu_clockMode.current()].fs/1000), zero_phase=True)
            # Calculate I/Q offsets
            IoffsetArr[j,i] = (np.amax(Idown) + np.amin(Idown))/2
            QoffsetArr[j,i] = (np.amax(Qdown) + np.amin(Qdown))/2
            # Calculate I/Q gain
            IQgainArr[j,i] = (np.amax(Idown) - np.amin(Idown))/(np.amax(Qdown) - np.amin(Qdown))
        
        gui.Ioffset[i] = np.round(np.median(IoffsetArr[:,i]), precision)
        gui.Qoffset[i] = np.round(np.median(QoffsetArr[:,i]), precision)
        gui.IQgain[i] = np.round(np.median(IQgainArr[:,i]), precision)
        print('Offset (Laser ' + str(i+1) + ') = ' + str(gui.Ioffset[i]) + '/' + str(gui.Qoffset[i]))
        print('Gain (Laser ' + str(i+1) + ') = ' + str(gui.IQgain[i]))   
        gui.textWindow.insert(tk.END, 'Laser ' + str(i+1) + ': I Offset = ' + str(gui.Ioffset[i]) + '\n')
        gui.textWindow.insert(tk.END, 'Laser ' + str(i+1) + ': Q Offset = ' + str(gui.Qoffset[i]) + '\n')
        gui.textWindow.insert(tk.END, 'Laser ' + str(i+1) + ': I/Q Gain = ' + str(gui.IQgain[i]) + '\n')
        gui.textWindow.see(tk.END)
        gui.update()
        
        gui.progressBar.step(0.1)
        gui.progressBar.update()
    
    
    # Disable dither
    gui.InterrogatorHandle.interrogators[gui.popupMenu_clockMode.current()].disableDither()
    

##################################################################################
# AUXILIARY FUNCTIONS
##################################################################################   

# Find optimal DAS sampling frequency based on DAS sensing channel range
def optimizeDASfs(gui):

    print('Optimizing DAS sampling frequency ... ', end='')
    gui.textWindow.insert(tk.END, 'Optimizing DAS sampling frequency ... ')

    # Remote Circulator Case
    if len(gui.fiberSensingRegions) > 1:

        # Get maximum DAS pulse repetition rate
        sumSensingChanns = (gui.fiberSensingRegions[0][1]-gui.fiberSensingRegions[0][0]+1) + (gui.fiberSensingRegions[-1][1]-gui.fiberSensingRegions[1][0]+1)
        maxPulseRepRate = getTs(gui, sumSensingChanns,1)

        # Calculate upper limit of light pulses that can traverse the fiber at the same time
        maxNumPulses = int(gui.fiberSensingRegions[-1][1]/maxPulseRepRate)

        # Optimize DAS pulse repetition rate
        success = 0
        while success == 0:
            minPulseRepRate = getTs(gui, (gui.fiberSensingRegions[-1][1] - gui.fiberSensingRegions[0][0])/(maxNumPulses+1), 1)
            if maxNumPulses > 0:
                maxPulseRepRate = getTs(gui, (gui.fiberSensingRegions[1][0] - gui.fiberSensingRegions[0][1])/maxNumPulses, 0)
            else:
                maxPulseRepRate = minPulseRepRate
            
            if maxPulseRepRate >= minPulseRepRate:
                success = 1
            else:
                maxNumPulses = maxNumPulses - 1

    # Continuous Sensing Fiber Case
    elif len(gui.fiberSensingRegions) == 1:
        # Get maximum DAS pulse repetition rate
        sumSensingChanns = (gui.fiberSensingRegions[0][1]-gui.fiberSensingRegions[0][0]+1)
        minPulseRepRate = getTs(gui, sumSensingChanns,1)
        
    for i in range(len(gui.InterrogatorHandle.dict_ts2fs)):
        if gui.InterrogatorHandle.dict_ts2fs[i][0] == minPulseRepRate:
            fs = gui.InterrogatorHandle.dict_ts2fs[i][1]        
    
    print(' success (' + str(fs) + ' Hz)')
    gui.textWindow.insert(tk.END, 'success (' + str(fs/1000) + ' kHz)\n')
    gui.textWindow.see(tk.END)

    return(fs)

# Get DAS pulse repetition rate as a function of the number of DAS sensing channels
def getTs(gui, chann, flag):

    # Get lower DAS pulse repetition rate
    if flag == 0:
        ind = [x for x in range(len(gui.InterrogatorHandle.dict_ts2fs)) if (gui.InterrogatorHandle.dict_ts2fs[x][0] - chann) < 0]
        if not ind:
            ts = 0
        else:
            ts = gui.InterrogatorHandle.dict_ts2fs[ind[-1]][0]
    # Get higher DAS pulse repetition rate    
    elif flag == 1:
        ind = [x for x in range(len(gui.InterrogatorHandle.dict_ts2fs)) if (gui.InterrogatorHandle.dict_ts2fs[x][0] - chann) > 0]
        ts = gui.InterrogatorHandle.dict_ts2fs[ind[0]][0]

    return(ts)

def generateOscilloscopePlot(gui, interrogator, laserNum, firstChann, lastChann):
    
    # Recording parameters
    recLen = 0.1 # Record length in seconds
    # Acquire data
    [data, firstChann, lastChann] = dataAcq.getData(gui, firstChann, lastChann, recLen, laserNum)
    # Extract I/Q data for first laser pulse from data buffer
    I = data[interrogator.boardNum][0,0:-2:2]
    Q = data[interrogator.boardNum][0,1:-1:2]
    # Calculate the I/Q radius
    IQrad = np.sqrt(I*I+Q*Q)
    # Generate plots
    ax1 = plt.subplot(311)
    plt.plot(np.arange(firstChann, lastChann), I, color='C' + str(laserNum-1))
    plt.ylabel('I')
    plt.ylim(-1, +1)
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.grid(True)
    ax2 = plt.subplot(312)
    plt.plot(np.arange(firstChann, lastChann), Q, color='C' + str(laserNum-1))
    plt.ylabel('Q')
    plt.ylim(-1, +1)
    plt.setp(ax2.get_xticklabels(), visible=False)
    plt.grid(True)
    ax3 = plt.subplot(313)
    plt.plot(np.arange(firstChann, lastChann), IQrad, color='C' + str(laserNum-1))
    plt.ylabel('I/Q Radius')
    plt.xlabel('Channel')
    plt.ylim(0, +1.5)
    plt.grid(True)
    plt.suptitle(interrogator.name + ' Oscilloscope Plot - Laser ' + str(laserNum) + ': GL ' + str(gui.InterrogatorHandle.interrogators[gui.popupMenu_DASinterrogator.current()].gaugeLength) + 'm', fontweight= 'bold')
    gui.calibResultsPdf.savefig()
    plt.close()
        
