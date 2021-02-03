# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 10:41:40 2017

@author: H131339
"""

import math
import ctypes
import atsapi as ats
import numpy as np
import os
import time

def getData(gui, firstChann, lastChann, recLen, laserNum):


    # Make sure that boardHandles[0] is the system's master
    if gui.DigitizerHandle.boardHandles[0].boardId != 1:
        raise ValueError("The first board passed should be the master.")
    for board in gui.DigitizerHandle.boardHandles:
        if board.systemId != gui.DigitizerHandle.boardHandles[0].systemId:
            raise ValueError("All the boards should be of the same system.")

    # Trigger offset needs to be a multiple of 8
    channOffset = firstChann - 1
    if (8 * math.floor(channOffset/8) != channOffset):
        channOffset = 8 * math.floor(channOffset/8)
    # Number of recorded channels needs to be a multiple of 32
    postTriggerSamples = lastChann - channOffset
    if math.fmod(postTriggerSamples, 32) != 0:
        postTriggerSamples = 32 * math.ceil(postTriggerSamples/32)
    firstChann = channOffset + 1
    lastChann = postTriggerSamples + channOffset
    
    # Set number of pre-trigger samples to 0
    preTriggerSamples = 0
    
    # Set number of buffers
    bufferCount = 20
    # Set number of records per channel and buffer such that all buffers contain 1 second of data
    recordsPerBuffer = round(gui.InterrogatorHandle.fs/bufferCount)
    
    # Specify buffer timeout
    bufferTimeout = 5000
    
    # Set number of channels used during acquisition
    if laserNum == 1:
        numChannels = 2
        channelMask = 3
    elif laserNum == 2:
        numChannels = 2
        channelMask = 12
    elif laserNum == 3:
        numChannels = 4
        channelMask = 15
        
    # Calculate the size of each buffer in bytes
    [maxSamplesPerRecord, bitsPerSample] = gui.DigitizerHandle.boardHandles[0].getChannelInfo()
    bytesPerSample = math.floor((bitsPerSample.value + 7) / 8)
    samplesPerBuffer = postTriggerSamples * recordsPerBuffer * numChannels
    bytesPerBuffer = bytesPerSample * samplesPerBuffer
    
    
    buffers = []
    data = []
    for b in range(len(gui.DigitizerHandle.boardHandles)):  
        # Set time (in sample clocks) to wait after receiving a trigger event before capturing a record for the trigger    
        gui.DigitizerHandle.boardHandles[b].setTriggerDelay(channOffset)
        # Create array of DMA buffers
        buffers.append([])
        for i in range(bufferCount):
            buffers[b].append(ats.DMABuffer(ctypes.c_uint16, bytesPerBuffer))
        # Set the record size
        gui.DigitizerHandle.boardHandles[b].setRecordSize(preTriggerSamples, postTriggerSamples)
        # Configure board to make continuous AutoDMA acquisition
        admaFlags = ats.ADMA_EXTERNAL_STARTCAPTURE | ats.ADMA_NPT | ats.ADMA_INTERLEAVE_SAMPLES
        recordsPerAcquisition = (2**31)-1
        gui.DigitizerHandle.boardHandles[b].beforeAsyncRead(channelMask, preTriggerSamples, postTriggerSamples, recordsPerBuffer, recordsPerAcquisition, admaFlags)
        # Post DMA buffers to board
        for i in buffers[b]:
            gui.DigitizerHandle.boardHandles[b].postAsyncBuffer(i.addr, i.size_bytes)
        
        # Initialize matrix holding data
        data.append(np.zeros((int(recLen*gui.InterrogatorHandle.fs), (numChannels*postTriggerSamples)), dtype=int))

    # Start acquisition
    gui.DigitizerHandle.boardHandles[0].startCapture()
    
    buffersCompleted = 0
    for i in range(int(recLen*bufferCount)):

        for b in range(len(gui.DigitizerHandle.boardHandles)):
        
            buffer = buffers[b][buffersCompleted % bufferCount]
            gui.DigitizerHandle.boardHandles[b].waitAsyncBufferComplete(buffer.addr, bufferTimeout)
       
            # Reshape data
            # Original: [A1, B1, C1, D1, A2, B2, C2, D2, ... A512, B512, C512, D512, ... A1, B1, C1, D1, ... A512, B512, C512, D512]
            # 1st step: [A1, B1, C1, D1, A2, B2, C2, D2, ... A512, B512, C512, D512
            #            A1, B1, C1, D1, A2, B2, C2, D2, ... A512, B512, C512, D512]  
            data[b][int(i*(gui.InterrogatorHandle.fs/bufferCount)):int((i+1)*(gui.InterrogatorHandle.fs/bufferCount)),:] = buffer.buffer.reshape(recordsPerBuffer, postTriggerSamples*numChannels)
            # Make the buffer available to be filled again by the board
            gui.DigitizerHandle.boardHandles[b].postAsyncBuffer(buffer.addr, buffer.size_bytes)
        
        buffersCompleted += 1
        
    # Abort the acquisition
    for b in range(len(gui.DigitizerHandle.boardHandles)):
        gui.DigitizerHandle.boardHandles[b].abortAsyncRead()
        data[b] = (data[b] - 2**15) / 2**15
    
    return(data, firstChann, lastChann)


def storeDataToDisk(gui, firstChann, lastChann, recLen, laserNum):


    t = time.time()
    # Make sure that boardHandles[0] is the system's master
    if gui.DigitizerHandle.boardHandles[0].boardId != 1:
        raise ValueError("The first board passed should be the master.")
    for board in gui.DigitizerHandle.boardHandles:
        if board.systemId != gui.DigitizerHandle.boardHandles[0].systemId:
            raise ValueError("All the boards should be of the same system.")

    # Trigger offset needs to be a multiple of 8
    channOffset = firstChann - 1
    if (8 * math.floor(channOffset/8) != channOffset):
        channOffset = 8 * math.floor(channOffset/8)
    # Number of recorded channels needs to be a multiple of 32
    postTriggerSamples = lastChann - channOffset
    if math.fmod(postTriggerSamples, 32) != 0:
        postTriggerSamples = 32 * math.ceil(postTriggerSamples/32)
    firstChann = channOffset + 1
    lastChann = postTriggerSamples + channOffset
    
    # Set number of pre-trigger samples to 0
    preTriggerSamples = 0
    
    # Set number of buffers
    bufferCount = 10
    # Set number of records per channel and buffer such that all buffers contain 1 second of data
    recordsPerBuffer = round(gui.InterrogatorHandle.fs/bufferCount)
    
    # Specify buffer timeout
    bufferTimeout = 5000
    
    # Set number of channels used during acquisition
    if laserNum == 1:
        numChannels = 2
        channelMask = 3
    elif laserNum == 2:
        numChannels = 2
        channelMask = 12
    elif laserNum == 3:
        numChannels = 4
        channelMask = 15
        
    # Calculate the size of each buffer in bytes
    [maxSamplesPerRecord, bitsPerSample] = gui.DigitizerHandle.boardHandles[0].getChannelInfo()
    bytesPerSample = math.floor((bitsPerSample.value + 7) / 8)
    samplesPerBuffer = postTriggerSamples * recordsPerBuffer * numChannels
    bytesPerBuffer = bytesPerSample * samplesPerBuffer
    
    
    buffers = []
    data = []
    for b in range(len(gui.DigitizerHandle.boardHandles)):  
        # Set time (in sample clocks) to wait after receiving a trigger event before capturing a record for the trigger    
        gui.DigitizerHandle.boardHandles[b].setTriggerDelay(channOffset)
        # Create array of DMA buffers
        buffers.append([])
        for i in range(bufferCount):
            buffers[b].append(ats.DMABuffer(ctypes.c_uint16, bytesPerBuffer))
        # Set the record size
        gui.DigitizerHandle.boardHandles[b].setRecordSize(preTriggerSamples, postTriggerSamples)
        # Configure board to make continuous AutoDMA acquisition
        admaFlags = ats.ADMA_EXTERNAL_STARTCAPTURE | ats.ADMA_NPT | ats.ADMA_INTERLEAVE_SAMPLES
        recordsPerAcquisition = (2**31)-1
        gui.DigitizerHandle.boardHandles[b].beforeAsyncRead(channelMask, preTriggerSamples, postTriggerSamples, recordsPerBuffer, recordsPerAcquisition, admaFlags)
        # Post DMA buffers to board
        for i in buffers[b]:
            gui.DigitizerHandle.boardHandles[b].postAsyncBuffer(i.addr, i.size_bytes)
        
        # Initialize matrix holding data
        data.append(np.zeros((int(recLen*gui.InterrogatorHandle.fs), (numChannels*postTriggerSamples)), dtype=int))

    # Write record info to file
    createRecordingInfoFile(gui, firstChann, lastChann)
    
    # If RAW directory already exists, delete its content
    RAWdir = os.path.join(gui.daqRecDir.get(), 'RAW')
    if os.path.isdir(RAWdir):
        for fileName in os.listdir(RAWdir):
            os.unlink(os.path.join(RAWdir, fileName))
    # Otherwise, create RAW directory
    else:
        os.mkdir(RAWdir)

    # Start acquisition
    print('\n\nStarting Data Acquisition')
    gui.DigitizerHandle.boardHandles[0].startCapture()
    buffersCompleted = 0
    for i in range(int(recLen*bufferCount)):

        if i % bufferCount is 0:
            print(str(int(i/bufferCount)+1) + ' s')
            if buffersCompleted > 0:
                dataFid.close()
            fileName = 'data' + '{:04d}'.format(int(i/bufferCount)+1) + '.bin'
            dataFid = open(os.path.join(RAWdir, fileName), 'w')

        for b in range(len(gui.DigitizerHandle.boardHandles)):
        
            buffer = buffers[b][buffersCompleted % bufferCount]
            gui.DigitizerHandle.boardHandles[b].waitAsyncBufferComplete(buffer.addr, bufferTimeout)

            # Save data to disk
            buffer.buffer.tofile(dataFid)
            
            # Make the buffer available to be filled again by the board
            gui.DigitizerHandle.boardHandles[b].postAsyncBuffer(buffer.addr, buffer.size_bytes)
        
        buffersCompleted += 1
        
    # Abort the acquisition
    for b in range(len(gui.DigitizerHandle.boardHandles)):
        gui.DigitizerHandle.boardHandles[b].abortAsyncRead()
    
    dataFid.close()
    print('Data Acquisition Complete\n')
    
    

# Function returns channel range supported by ATS9440 digitizer
def getChannRange(firstChann, lastChann):
    
    # Trigger offset needs to be a multiple of 8
    channOffset = firstChann - 1
    if (8 * math.floor(channOffset/8) != channOffset):
        channOffset = 8 * math.floor(channOffset/8)
    # Number of recorded channels needs to be a multiple of 32
    postTriggerSamples = lastChann - channOffset
    if math.fmod(postTriggerSamples, 32) != 0:
        postTriggerSamples = 32 * math.ceil(postTriggerSamples/32)
    firstChann = channOffset + 1
    lastChann = postTriggerSamples + channOffset
    
    return(firstChann, lastChann)

# Function that creates the recording info file
# Line 1: Number of Interrogators
# Line 2: First DAS Channel
# Line 3: Last DAS Channel
# Line 4: DAS Sampling Frequency
# Line 5: Gauge Length
# Line 6-9: ITU Channels 
def createRecordingInfoFile(gui, firstChann, lastChann):
    
    fileName = os.path.join(gui.daqRecDir.get(), 'recInfo.txt')
    fid = open(fileName, 'w')
    fid.write(str(len(gui.DigitizerHandle.boardHandles)) + '\n') # Number of Interrogators
    fid.write(str(firstChann) + '\n') # First DAS Channel
    fid.write(str(lastChann) + '\n') # Last DAS Channel
    fid.write(str(gui.InterrogatorHandle.fs) + '\n') # DAS Sampling Frequency
    fid.write(str(gui.InterrogatorHandle.interrogators[gui.popupMenu_DASinterrogator.current()].gaugeLength) + '\n') # Gauge Length
    if len(gui.DigitizerHandle.boardHandles) == 1: # ITU Channels
        fid.write(str(gui.InterrogatorHandle.interrogators[gui.popupMenu_DASinterrogator.current()].laserITU[0]) + '\n')
        fid.write(str(gui.InterrogatorHandle.interrogators[gui.popupMenu_DASinterrogator.current()].laserITU[1]))
    else:
        fid.write(str(gui.InterrogatorHandle.interrogators[0].laserITU[0]) + '\n')
        fid.write(str(gui.InterrogatorHandle.interrogators[0].laserITU[1]) + '\n')
        fid.write(str(gui.InterrogatorHandle.interrogators[1].laserITU[0]) + '\n')
        fid.write(str(gui.InterrogatorHandle.interrogators[1].laserITU[1]))

    fid.close()


