# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 14:32:02 2017

@author: H131339
"""

from __future__ import division
from math import floor

import atsapi as ats

class digitizer:
    
    # Alazar board handles
    boardHandles = []
    # Clock Mode
    # 0: 100MHz External CRI Clock (Default)
    # 1: 10MHz External CRI Clock
    # 2: 100MHz Internal Clock 
    clockMode = 0
    # Trigger Mode
    # 1: Rising Edge
    # 2: Falling Edge (Default)
    triggerMode = 2 
    # Digitizer status
    # 0: Ready
    # 1: Not ready
    status = 0
    # I/O Port input range
    IOinputRange = 2 # Set by default to 2V
    
    # Constructor
    def __init__(self, systemID=1, numInterrogators=1):
        
        for i in range(min(numInterrogators, ats.boardsInSystemBySystemID(systemID))):
            self.boardHandles.append(ats.Board(systemID, i+1))        
        for board in self.boardHandles:
            self.ConfigBoard(board, self.clockMode, self.triggerMode)

    # Configure Board    
    def ConfigBoard(self, board, clockMode, triggerMode):

        # Configure Clock
        self.ConfigClock(board, self.clockMode)
        # Configure I/O ports
        self.ConfigIOPorts(board, self.IOinputRange)
        # Configure Trigger
        self.ConfigTrigger(board, self.triggerMode)
        
    # Configure Clock    
    def ConfigClock(self, boardHandle, clockMode):
        
        if clockMode == 0: # 100 MHz External Clock
            print('Digitizer Clock Mode: 100 MHz DAS Interrogator Clock')
            try:
                boardHandle.setCaptureClock(ats.FAST_EXTERNAL_CLOCK,   # 100MHz PLL external clock mode
                                                 ats.SAMPLE_RATE_USER_DEF,  # Sampling rate is 100MHz/s
                                                 ats.CLOCK_EDGE_RISING,     # Sampling coincides with clock rising edge
                                                 1)                         # Clock Decimation set to 1
                # Disable AUX 2 port
                boardHandle.configureAuxIO(ats.AUX_OUT_SERIAL_DATA, 0)
                self.status = 0
            except:
                print('Alazar Set Capture Clock Error: Please make sure DAS Interrogator is turned on and connected to Data Acquisition Server')
                self.status = 1
            
        elif clockMode == 1: # 10 MHz External Clock
            print('Digitizer Clock Mode: 10 MHz DAS Interrogator Clock')
            try:
                boardHandle.setCaptureClock(ats.EXTERNAL_CLOCK_10MHz_REF,  # 10MHz PLL external clock mode  
                                                 100.e6,                        # Sampling rate is 100MHz/s
                                                 ats.CLOCK_EDGE_RISING,         # Sampling coincides with clock rising edge
                                                 1)                             # Clock Decimation set to 1
                # Disable AUX 2 port
                boardHandle.configureAuxIO(ats.AUX_OUT_SERIAL_DATA, 0)
                self.status = 0
            except:
                print('Alazar Set Capture Clock Error: Please make sure CRI Interrogator is turned on and connected to Data Acquisition Server')
                self.status = 1
                
        elif clockMode == 2: # 100 MHz Internal Clock
            print('Digitizer Clock Mode: 25 MHz ATS Digitizer Clock')
            boardHandle.setCaptureClock(ats.INTERNAL_CLOCK,        # 10MHz PLL external clock mode 
                                             ats.SAMPLE_RATE_100MSPS,   # Sampling rate is 100MHz/s
                                             ats.CLOCK_EDGE_RISING,     # Sampling coincides with clock rising edge
                                             1)                         # Clock Decimation set to 1
            # Configure AUX 2 to output clock signal at 25 MHz
            boardHandle.configureAuxIO(ats.AUX_OUT_PACER,
                                                          4)
            self.status = 0
                
        self.clockMode = clockMode
                
                
    # Configure I/O ports
    def ConfigIOPorts(self, boardHandle, IOinputRange):
        
        if IOinputRange == 1:
            atsIOinputRange = ats.INPUT_RANGE_PM_1_V
        elif IOinputRange == 2:
            atsIOinputRange = ats.INPUT_RANGE_PM_2_V
        elif IOinputRange == 4:
            atsIOinputRange = ats.INPUT_RANGE_PM_4_V
        elif IOinputRange == 5:
            atsIOinputRange = ats.INPUT_RANGE_PM_5_V
        else:
            print('Unsupported inpute range voltage setting. Defaulting to 2V')
            atsIOinputRange = ats.INPUT_RANGE_PM_2_V
            
        # Channel A (I Channel - Laser 1)
        boardHandle.inputControlEx(ats.CHANNEL_A,          # Input Channel
                                        ats.DC_COUPLING,        # Input Coupling
                                        atsIOinputRange,        # Input range
                                        ats.IMPEDANCE_50_OHM)   # Input Impedance
        
        # Channel B (Q Channel - Laser 1)
        boardHandle.inputControlEx(ats.CHANNEL_B,          # Input Channel
                                        ats.DC_COUPLING,        # Input Coupling
                                        atsIOinputRange,        # Input range
                                        ats.IMPEDANCE_50_OHM)   # Input Impedance
        # Channel C (I Channel - Laser 2)
        boardHandle.inputControlEx(ats.CHANNEL_C,          # Input Channel
                                        ats.DC_COUPLING,        # Input Coupling
                                        atsIOinputRange,        # Input range
                                        ats.IMPEDANCE_50_OHM)   # Input Impedance
        
        # Channel D (Q Channel - Laser 2)
        boardHandle.inputControlEx(ats.CHANNEL_D,          # Input Channel
                                        ats.DC_COUPLING,        # Input Coupling
                                        atsIOinputRange,        # Input range
                                        ats.IMPEDANCE_50_OHM)   # Input Impedance
        
        self.IOinputRange = IOinputRange
    
    # Configure Trigger
    def ConfigTrigger(self, boardHandle, triggerMode):
        
        
        if triggerMode == 1:
            atsTriggerMode = ats.TRIGGER_SLOPE_POSITIVE
            print('Trigger Mode: Rising Edge')
        elif triggerMode == 2:
            atsTriggerMode = ats.TRIGGER_SLOPE_NEGATIVE
            print('Trigger Mode: Falling Edge')
        
        # Calculate trigger level
        triggerRange_V = 5 # Trigger range in Volts
        triggerLevel_V = 0.6 # Trigger level in Volts
        triggerLevel = 128 + floor(127 * triggerLevel_V/triggerRange_V) # Trigger Level corresponding to 12% expressed in the range from 0 to 255         
        
        # Configure Trigger Engine J                          
        boardHandle.setTriggerOperation(ats.TRIG_ENGINE_OP_J,  # Trigger Operation
                                             ats.TRIG_ENGINE_J,     # Trigger Engine ID
                                             ats.TRIG_EXTERNAL,     # Trigger Source Port
                                             atsTriggerMode,           # Trigger Mode (Rising Edge vs. Falling Edge Triggering)
                                             triggerLevel,          # Trigger Level
                                             ats.TRIG_ENGINE_K,     # Triger Engine ID
                                             ats.TRIG_DISABLE,      # Trigger Source Port
                                             atsTriggerMode,           # Trigger Mode (Rising Edge vs. Falling Edge Triggering)
                                             triggerLevel)          # Trigger Level
        
        # Configure trigger input port
        boardHandle.setExternalTrigger(ats.DC_COUPLING,        # Input Coupling
                                            ats.ETR_5V)             # Input Range
        
        # Set trigger timeout
        boardHandle.setTriggerTimeOut(0) # Time Out in microseconds (0 = wait forever)
        
        self.triggerMode = triggerMode
        
        
        
        
        
        
        
        
    
    