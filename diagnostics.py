import tkinter as tk
import time
import numpy as np
import math
import os
import psutil
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pylab
import sys
import gc
import scipy.signal as signal

import dataAcq
import IQtoPhase
import transforms as transforms


##################################################################################
# ACOUSTIC NOISE FLOOR TEST
##################################################################################
def AcousticNoiseFloorTest(gui):

    gui.textWindow.insert(tk.END, 'Starting Acoustic Noise Floor Test\n')
    gui.textWindow.see(tk.END)
    gui.progressBar.update()
    
    # HAL internal Acoustic Noise Floor Procedure
    if gui.selectedDiagnosticsFormat.get() == 1:

        
        gui.textWindow.insert(tk.END, 'HAL Internal Test Procedure\n')
        gui.textWindow.see(tk.END)
        noiseFloor = getAcousticNoiseFloor_HAL(gui, gui.diagnostics.acousticNoiseFloor.testDur, gui.diagnostics.acousticNoiseFloor.channRange[0], gui.diagnostics.acousticNoiseFloor.freqRange)

        dataSize = noiseFloor.shape
        medianNoiseFloor = []
        print('\n')
        for i in range(dataSize[0]):
            medianNoiseFloor.append(np.median(noiseFloor[i,:,:]))

        if dataSize[0] == 3: # Single DAS interrogator acquisition mode
            generateNoiseFloorHistograms(gui, gui.InterrogatorHandle.interrogators[0].name, noiseFloor[0,:,:], 0)
            generateNoiseFloorHistograms(gui, gui.InterrogatorHandle.interrogators[0].name, noiseFloor[1,:,:], 1)
            generateNoiseFloorHistograms(gui, gui.InterrogatorHandle.interrogators[0].name, noiseFloor[2,:,:], 2)
            print(gui.InterrogatorHandle.interrogators[0].name + ' Acoustic Noise Floor - Laser 1:   ' + str(medianNoiseFloor[0]) + 'dB')
            print(gui.InterrogatorHandle.interrogators[0].name + ' Acoustic Noise Floor - Laser 2:   ' + str(medianNoiseFloor[1]) + 'dB')
            print(gui.InterrogatorHandle.interrogators[0].name + ' Acoustic Noise Floor - Laser 1+2: ' + str(medianNoiseFloor[2]) + 'dB')
            gui.textWindow.insert(tk.END, gui.InterrogatorHandle.interrogators[0].name + ' Acoustic Noise Floor - Laser 1:   {0:.2f} dB\n'.format(medianNoiseFloor[0]))
            gui.textWindow.insert(tk.END, gui.InterrogatorHandle.interrogators[0].name + ' Acoustic Noise Floor - Laser 2:   {0:.2f} dB\n'.format(medianNoiseFloor[1]))
            gui.textWindow.insert(tk.END, gui.InterrogatorHandle.interrogators[0].name + ' Acoustic Noise Floor - Laser 1+2: {0:.2f} dB\n'.format(medianNoiseFloor[2]))
        else: # Dual DAS interrogator acquisition mode
            generateNoiseFloorHistograms(gui, gui.InterrogatorHandle.interrogators[0].name, noiseFloor[0,:,:], 0)
            generateNoiseFloorHistograms(gui, gui.InterrogatorHandle.interrogators[0].name, noiseFloor[1,:,:], 1)
            generateNoiseFloorHistograms(gui, gui.InterrogatorHandle.interrogators[1].name, noiseFloor[2,:,:], 0)
            generateNoiseFloorHistograms(gui, gui.InterrogatorHandle.interrogators[1].name, noiseFloor[3,:,:], 1)
            generateNoiseFloorHistograms(gui, gui.InterrogatorHandle.interrogators[0].name, noiseFloor[4,:,:], 2)
            generateNoiseFloorHistograms(gui, gui.InterrogatorHandle.interrogators[1].name, noiseFloor[5,:,:], 2)
            generateNoiseFloorHistograms(gui, gui.InterrogatorHandle.interrogators[1].name, noiseFloor[6,:,:], 4)
            print(gui.InterrogatorHandle.interrogators[0].name + ' Acoustic Noise Floor - Laser 1:   ' + str(medianNoiseFloor[0]) + 'dB')
            print(gui.InterrogatorHandle.interrogators[0].name + ' Acoustic Noise Floor - Laser 2:   ' + str(medianNoiseFloor[1]) + 'dB')
            print(gui.InterrogatorHandle.interrogators[1].name + ' Acoustic Noise Floor - Laser 1:   ' + str(medianNoiseFloor[2]) + 'dB')
            print(gui.InterrogatorHandle.interrogators[1].name + ' Acoustic Noise Floor - Laser 2:   ' + str(medianNoiseFloor[3]) + 'dB')
            print(gui.InterrogatorHandle.interrogators[0].name + ' Acoustic Noise Floor - Laser 1+2: ' + str(medianNoiseFloor[4]) + 'dB')
            print(gui.InterrogatorHandle.interrogators[1].name + ' Acoustic Noise Floor - Laser 1+2: ' + str(medianNoiseFloor[5]) + 'dB')
            print(gui.InterrogatorHandle.interrogators[0].name + ' & ' + gui.InterrogatorHandle.interrogators[1].name + ' Acoustic Noise Floor - Laser 1+2+3+4: ' + str(medianNoiseFloor[6]) + 'dB')
            gui.textWindow.insert(tk.END, gui.InterrogatorHandle.interrogators[0].name + ' Acoustic Noise Floor - Laser 1:   {0:.2f}  dB\n'.format(medianNoiseFloor[0]))
            gui.textWindow.insert(tk.END, gui.InterrogatorHandle.interrogators[0].name + ' Acoustic Noise Floor - Laser 2:   {0:.2f}  dB\n'.format(medianNoiseFloor[1]))
            gui.textWindow.insert(tk.END, gui.InterrogatorHandle.interrogators[1].name + ' Acoustic Noise Floor - Laser 1:   {0:.2f}  dB\n'.format(medianNoiseFloor[2]))                
            gui.textWindow.insert(tk.END, gui.InterrogatorHandle.interrogators[1].name + ' Acoustic Noise Floor - Laser 2:   {0:.2f}  dB\n'.format(medianNoiseFloor[3]))
            gui.textWindow.insert(tk.END, gui.InterrogatorHandle.interrogators[0].name + ' Acoustic Noise Floor - Laser 1+2: {0:.2f}  dB\n'.format(medianNoiseFloor[4]))
            gui.textWindow.insert(tk.END, gui.InterrogatorHandle.interrogators[1].name + ' Acoustic Noise Floor - Laser 1+2: {0:.2f}  dB\n'.format(medianNoiseFloor[5])) 
            gui.textWindow.insert(tk.END, 'Acoustic Noise Floor - Laser 1+2+3+4: {0:.2f}  dB\n'.format(medianNoiseFloor[6])) 

        gui.progressBar.update()
        gui.textWindow.see(tk.END)

    # SEAFOM Acoustic Noise Floor Procedure
    else:

        gui.textWindow.insert(tk.END, 'SEAFOM Test Procedure\n')
        gui.textWindow.see(tk.END)
        gui.diagnostics.acousticNoiseFloor.channRange = [[401, 700], [2301, 2600], [4201, 4500]]

        # Initialize matrix holding acoustic noise floor results
        medianNoiseFloor = [[0,0,0], [0,0,0],[0,0,0]]
        
        for i in range(0,len(gui.diagnostics.acousticNoiseFloor.channRange)):
            medianNoiseFloor[i] = getAcousticNoiseFloor_SEAFOM(gui, gui.diagnostics.acousticNoiseFloor.testDur, gui.diagnostics.acousticNoiseFloor.channRange[i], gui.diagnostics.acousticNoiseFloor.freqRange)

            print('\n')
            print('Channel Range: ' + str(gui.diagnostics.acousticNoiseFloor.channRange[i][0]) + ':' + str(gui.diagnostics.acousticNoiseFloor.channRange[i][1]))
            print('Acoustic Noise Floor - Laser 1:   ' + str(medianNoiseFloor[i][0]) + 'dB')
            print('Acoustic Noise Floor - Laser 2:   ' + str(medianNoiseFloor[i][1]) + 'dB')
            print('Acoustic Noise Floor - Laser 1+2: ' + str(medianNoiseFloor[i][2]) + 'dB')

            gui.textWindow.insert(tk.END, '\nChannel Range: ' + str(gui.diagnostics.acousticNoiseFloor.channRange[i][0]) + ':' + str(gui.diagnostics.acousticNoiseFloor.channRange[i][1]) + '\n')
            gui.textWindow.insert(tk.END, 'Acoustic Noise Floor - Laser 1:   {0:.2f} dB\n'.format(medianNoiseFloor[i][0]))
            gui.textWindow.insert(tk.END, 'Acoustic Noise Floor - Laser 2:   {0:.2f} dB\n'.format(medianNoiseFloor[i][1]))
            gui.textWindow.insert(tk.END, 'Acoustic Noise Floor - Laser 1+2: {0:.2f} dB\n'.format(medianNoiseFloor[i][2]))
            gui.progressBar.update()
            gui.textWindow.see(tk.END)

    return(medianNoiseFloor)




def getAcousticNoiseFloor_HAL(gui, testDur, channRange, freqRange):
    
     # Recording parameters
    recLen = 1 # Length in seconds for which a single acoustic noise floor measurement with be calculated
    
    # Acoustic Noise Floor
    [firstChann, lastChann] = dataAcq.getChannRange(channRange[0], channRange[1])
    channOffset = [channRange[0] - firstChann, lastChann- channRange[1]]
    # Initialize matrix holding noise floor numbers
    if len(gui.InterrogatorHandle.interrogators) == 1: # Single DAS interrogator data acquisition mode
        noiseFloorMat = np.zeros((3, testDur, channRange[1] - channRange[0] + 1))
    else: # Dual DAS interrogator data acquisition mode
        noiseFloorMat = np.zeros((7, testDur, channRange[1] - channRange[0] + 1))

    
    for i in range(0,testDur):

        print('Acquiring data (' + str(i+1) + '/' + str(testDur) + ')')
        gui.progressBar.step(1/testDur)
        gui.progressBar.update()

        # Acquire data
        [data, firstChann, lastChann] = dataAcq.getData(gui, firstChann, lastChann, recLen, 3)
        
        dataSize = data[0].shape
         # Extract I/Q data from data buffer for each laser
        I = []
        Q = []
        for j in range(len(data)):
            I.append(data[j][:, (channOffset[0]*4):(dataSize[1]-3-channOffset[1]*4):4])
            I.append(data[j][:, (2+channOffset[0]*4):(dataSize[1]-1-channOffset[1]*4):4])
            Q.append(data[j][:, (1+channOffset[0]*4):(dataSize[1]-2-channOffset[1]*4):4])
            Q.append(data[j][:, (3+channOffset[0]*4):(dataSize[1]-channOffset[1]*4):4])
    
        dataSize = I[0].shape     
        
        for j in range(0,dataSize[1]):
            
            n = 0
            # Get noise floor of individual lasers
            for k in range(len(I)):
                phaseData = IQtoPhase.getPhaseData(I[k][:,j],Q[k][:,j])
                [P,F] = transforms.periodogram(phaseData, gui.InterrogatorHandle.fs)
                P = 10*np.log10(P)
                ind1 = np.nonzero(np.floor(F) == freqRange[0])
                ind2 = np.nonzero(np.floor(F) == freqRange[1])
                ind1 = np.ravel(ind1)
                ind2 = np.ravel(ind2)
                noiseFloorMat[n, i, j] = np.median(P[ind1[0]:ind2[0]]) 
                n = n + 1
              
            # Get noise floor for each DAS interrogator (dual-laser)
            for k in range(len(gui.InterrogatorHandle.interrogators)):
                weightedPhaseData = IQtoPhase.getWeightedPhaseData([I[2*k], I[2*k+1]], [Q[2*k], Q[2*k+1]], j)
                [P,F] = transforms.periodogram(weightedPhaseData, gui.InterrogatorHandle.fs)
                P = 10*np.log10(P)
                noiseFloorMat[n, i, j] = np.median(P[ind1[0]:ind2[0]])
                n = n + 1

            # Get noise floor for DAS interrogator assembly (quad-laser)
            if len(gui.InterrogatorHandle.interrogators) == 2:
                weightedPhaseData = IQtoPhase.getWeightedPhaseData(I, Q, j)
                [P,F] = transforms.periodogram(weightedPhaseData, gui.InterrogatorHandle.fs)
                P = 10*np.log10(P)
                noiseFloorMat[n, i, j] = np.median(P[ind1[0]:ind2[0]])
                
                  
    return(noiseFloorMat)



##################################################################################
# ACOUSTIC NOISE FLOOR TEST - SEAFOM
##################################################################################
def getAcousticNoiseFloor_SEAFOM(gui, testDur, channRange, freqRange):
    
     # Recording parameters
    recLen = 1 # Length in seconds for which a single acoustic noise floor measurement with be calculated
    refractiveInd = 1.4682 # Refractive Index of SMF-28e

    # Acoustic Noise Floor
    [firstChann, lastChann] = dataAcq.getChannRange(channRange[0], channRange[1])
    channOffset = [channRange[0] - firstChann, lastChann- channRange[1]]
    noiseFloorMat = [0, 0, 0]
    
    strainDataFFT_avg = np.zeros((3, int(gui.InterrogatorHandle.fs/2)))

    for i in range(0,testDur):

        print('Acquiring data (' + str(i+1) + '/' + str(testDur) + ')')
        gui.progressBar.step(1/testDur)
        gui.progressBar.update()

        # Acquire data - Laser 1 & 2
        [data, firstChann, lastChann] = dataAcq.getData(gui, firstChann, lastChann, recLen, 3)
        dataSize = data[0].shape
        
         # Extract I/Q data from data buffer for each laser
        I = []
        Q = []
        for j in range(len(data)):
            I.append(data[j][:, (channOffset[0]*4):(dataSize[1]-3-channOffset[1]*4):4])
            I.append(data[j][:, (2+channOffset[0]*4):(dataSize[1]-1-channOffset[1]*4):4])
            Q.append(data[j][:, (1+channOffset[0]*4):(dataSize[1]-2-channOffset[1]*4):4])
            Q.append(data[j][:, (3+channOffset[0]*4):(dataSize[1]-channOffset[1]*4):4])
        
        dataSize = I[0].shape
        for j in range(0,dataSize[1]):
            
            # Noise FLoor - Laser 1
            phaseData = IQtoPhase.getPhaseData(I[0][:,j],Q[0][:,j])
            # Calculate the FFT according to the SEAFOM standard
            [phaseDataFFT, F] = transforms.seafom_fft(phaseData, gui.InterrogatorHandle.fs)
            # Convert from phase to pico strain
            strainDataFFT = IQtoPhase.phaseToStrain(phaseDataFFT, refractiveInd, gui.InterrogatorHandle.interrogators[gui.popupMenu_clockMode.current()].laserITU[0], gui.InterrogatorHandle.interrogators[gui.popupMenu_clockMode.current()].gaugeLength)
            strainDataFFT_avg[0,:] = strainDataFFT_avg[0,:] + strainDataFFT

            # Noise FLoor - Laser 2
            phaseData = IQtoPhase.getPhaseData(I[1][:,j],Q[1][:,j])
            # Calculate the FFT according to the SEAFOM standard
            [phaseDataFFT, F] = transforms.seafom_fft(phaseData, gui.InterrogatorHandle.fs)
            # Convert from phase to pico strain
            strainDataFFT = IQtoPhase.phaseToStrain(phaseDataFFT, refractiveInd, gui.InterrogatorHandle.interrogators[gui.popupMenu_clockMode.current()].laserITU[1], gui.InterrogatorHandle.interrogators[gui.popupMenu_clockMode.current()].gaugeLength)
            strainDataFFT_avg[1,:] = strainDataFFT_avg[1,:] + strainDataFFT

            # Noise FLoor - Laser 1 & 2
            phaseData = IQtoPhase.getWeightedPhaseData(I, Q, j)
            # Calculate the FFT according to the SEAFOM standard
            [phaseDataFFT, F] = transforms.seafom_fft(phaseData, gui.InterrogatorHandle.fs)
            # Convert from phase to pico strain
            strainDataFFT = IQtoPhase.phaseToStrain(phaseDataFFT, refractiveInd, gui.InterrogatorHandle.interrogators[gui.popupMenu_clockMode.current()].laserITU[0], gui.InterrogatorHandle.interrogators[gui.popupMenu_clockMode.current()].gaugeLength)
            strainDataFFT_avg[2,:] = strainDataFFT_avg[2,:] + strainDataFFT


    # Normalize the summed FFTs 
    strainDataFFT_avg[0,:] = strainDataFFT_avg[0,:]/(dataSize[1]*testDur)
    strainDataFFT_avg[1,:] = strainDataFFT_avg[1,:]/(dataSize[1]*testDur)
    strainDataFFT_avg[2,:] = strainDataFFT_avg[2,:]/(dataSize[1]*testDur)
    # Convert the data to log scale
    strainDataFFT_avg[0,:] = 20*np.log10(strainDataFFT_avg[0,:])
    strainDataFFT_avg[1,:] = 20*np.log10(strainDataFFT_avg[1,:])
    strainDataFFT_avg[2,:] = 20*np.log10(strainDataFFT_avg[2,:])

    # Calculate global acoustic noise floor measure
    ind1 = np.nonzero(np.floor(F) == freqRange[0])
    ind2 = np.nonzero(np.floor(F) == freqRange[1])
    ind1 = np.ravel(ind1)
    ind2 = np.ravel(ind2)
    noiseFloorMat[0] = np.median(strainDataFFT_avg[0,ind1[0]:ind2[0]])
    noiseFloorMat[1] = np.median(strainDataFFT_avg[1,ind1[0]:ind2[0]])
    noiseFloorMat[2] = np.median(strainDataFFT_avg[2,ind1[0]:ind2[0]])

    # Generate FFT plots
    generateFFTplots(gui, F, strainDataFFT_avg, channRange, noiseFloorMat)



    return(noiseFloorMat) 

            
 


##################################################################################
# ACOUSTIC NOISE FLOOR TEST
##################################################################################

def generateNoiseFloorHistograms(gui, name, noiseFloor, laserNum):

    # Calculate median noise floor
    acousticNoiseFloor = np.median(noiseFloor)

    # Generate histogram plot
    pylab.figure()
    pylab.hist(noiseFloor.flatten(), 50, density=1, histtype='bar', alpha=0.75, edgecolor='black',
               label= 'Median Acoustic Noise Floor: {0:.2f} dB'.format(acousticNoiseFloor))
    
    pylab.legend()

    pylab.xlabel('Noise Floor (dB)')

    if laserNum == 0 or laserNum == 1:
        pylab.title(name + ' - Noise Floor: Laser ' + str(laserNum + 1), fontweight= 'bold')
    elif laserNum == 2:
        pylab.title(name + ' - Noise Floor: Laser 1 & 2', fontweight= 'bold')
    else:
        pylab.title('Noise Floor: Laser 1 - 4', fontweight= 'bold')

    gui.diagnostics.resultsPdf.savefig()
    pylab.close()


# Function that generates the FFT plots for laser 1, laser 2 and laser 1+2 in pico strain per rt-Hz
def generateFFTplots(gui, F, noiseFloor, channRange, medNoiseFloor):

    ax1 = plt.subplot(311)
    noiseFloor_laser1_plt, = plt.plot(F, noiseFloor[0,:], color='C0', label='Median Noise Floor: {0:.2f} dB'.format(medNoiseFloor[0]))
    plt.legend(handles=[noiseFloor_laser1_plt], fontsize=8)
    plt.ylabel(r'$\frac{Pico Strain}{\sqrt{Hz}}$ [dB]')
    plt.grid('on')
    plt.title('Laser 1', fontsize=8)
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.xlim(0, gui.InterrogatorHandle.fs/2)
    ax2 = plt.subplot(312)
    noiseFLoor_laser2_plt, = plt.plot(F, noiseFloor[1,:], color='C1', label='Median Noise Floor: {0:.2f} dB'.format(medNoiseFloor[1]))
    plt.legend(handles=[noiseFLoor_laser2_plt], fontsize=8)
    plt.ylabel(r'$\frac{Pico Strain}{\sqrt{Hz}}$ [dB]')
    plt.grid('on')
    plt.title('Laser 2', fontsize=8)
    plt.setp(ax2.get_xticklabels(), visible=False)
    plt.xlim(0, gui.InterrogatorHandle.fs/2)
    ax3 = plt.subplot(313)
    noiseFloor_laser12_plt, = plt.plot(F, noiseFloor[2,:], color='C2', label='Median Noise Floor: {0:.2f} dB'.format(medNoiseFloor[2]))
    plt.legend(handles=[noiseFloor_laser12_plt], fontsize=8)
    plt.ylabel(r'$\frac{Pico Strain}{\sqrt{Hz}}$ [dB]')
    plt.xlabel('Frequency [Hz]')
    plt.grid('on')
    plt.title('Laser 1 & 2', fontsize=8)
    plt.xlim(0, gui.InterrogatorHandle.fs/2)
    plt.suptitle('DAS Acoustic Noise Floor: Gauge Length = ' + str(gui.InterrogatorHandle.interrogators[gui.popupMenu_clockMode.current()].gaugeLength) + 'm' + ' (Channels ' + str(channRange[0]) + '-' + str(channRange[1]) + ')')
    gui.diagnostics.resultsPdf.savefig()
    plt.close()