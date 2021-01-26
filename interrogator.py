# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 09:10:34 2017

@author: H131339
"""

import ctypes
from math import floor

class interrogatorAssembly:

    # List of interrogator objects
    interrogators = []
    # Data Acquisition Mode
    # 1 = Single DAS interrogator data acquisition (default)
    # 2 = Dual DAS interrogator data acquisition
    mode = 1
    # Names of interrogators
    interrogatorNames = []
    # Optical Pulse Repetition Rate in Hz
    fs  = 10000 # Default is 10 kHz
    # Optical Pulse Width
    pulseWidth = 20 # Default is 20 ns
    # Launch-side shutter delay (in clock cycles)
    shutterDelay = -12
    # Launch-side shutter Width (in clock cycles)
    shutterWidth = 24
    # Dictionary mapping pulse repetition rate to sampling frequency
    dict_ts2fs = [[2400, 40000],#[[2500, 40000],
                  [3025, 32000],
                  [3900, 25000], 
                  [4900, 20000],#[5000, 20000], 
                  [6150, 16000],#[6250, 16000], 
                  [7900, 12500],#[8000, 12500], 
                  [9900, 10000],#[10000, 10000], 
                  [12400, 8000],#[12500, 8000],
                  [19900, 5000],#[20000, 5000],
                  [24900, 4000],#[25000, 4000],
                  [31150, 3200],#[31250, 3200]]
                  [49900, 2000],
                  [62400, 1600]]

    # Constructor
    def __init__(self):
        
        # Load opcr.dll
        self.OPCRdll = ctypes.WinDLL('opcr.dll')
        
        # List unopened instruments
        unique_ID = ctypes.create_string_buffer(256)
        listLen = ctypes.c_int(0)
        errorCode = self.OPCRdll.List_Unopened_Instruments(unique_ID, ctypes.byref(listLen))
        if listLen.value == 0:
            print('Error: No Interrogator found. Make sure the interrogator is turned on and connected to the server')
            return
        elif listLen.value == 2:
            self.mode = 2
        elif listLen.value > 2:
            print('Error: More than two DAS interrogators found. Current software version only supports single or dual DAS interrogator data acquisition')
            return

        interrogatorNameList = unique_ID.value.decode('UTF-8')

        i = 0
        while interrogatorNameList.find('CRI-4400') != -1:
            ind = interrogatorNameList.find('CRI-4400')
            self.interrogators.append(self.interrogator(interrogatorNameList[ind:ind+13], i))
            self.interrogatorNames.append(interrogatorNameList[ind:ind+13])
            interrogatorNameList = interrogatorNameList[ind+14:]
            i = i + 1

        
        # Set sampling frequency of DAS interrogators
        self.status = self.setFs(self.fs)

        # Synchronize DAS interrogators
        if self.mode == 2:
            print('\nSynchronizing DAS interrogators ... ', end='')
            
            # For dual DAS interrogator setup, check that interrogator with lower serial number is set as master (first in list)
            serialNum1 = self.interrogators[0].name[-3:]
            serialNum2 = self.interrogators[1].name[-3:]
            if serialNum1 > serialNum2:
                # Swap interrogators in list
                self.interrogators[0], self.interrogators[1] = self.interrogators[1], self.interrogators[0]
                # Swap digitizer board numbers
                self.interrogators[0].boardNum = 0
                self.interrogators[1].boardNum = 1
                # Swap interrogator names
                self.interrogatorNames[0], self.interrogatorNames[1] = self.interrogatorNames[1], self.interrogatorNames[0]

            errorCode = self.synchronizeInterrogators()
            if errorCode == 0:
                print('success')
            else:
                print('failed')
              
        # Start pulsing of DAS interrogator
        errorCode = self.OPCRdll.Start_Timing(self.interrogators[0].opcr_handle)

    # Synchronize DAS interrogators
    def synchronizeInterrogators(self):
        errorCode = 0 
        ## Master DAS interrogator
        # Stop pulsing
        errorCode = self.OPCRdll.Stop_Timing(self.interrogators[0].opcr_handle)
        # Set Clk 2
        clk2Out = ctypes.c_int(0)
        errorCode = errorCode + self.OPCRdll.Set_Clock_2(self.interrogators[0].opcr_handle, clk2Out)
        # Set Timing Start Delay
        instrDelay = ctypes.c_int(1)
        fineDelay = ctypes.c_int(0)
        errorCode = errorCode + self.OPCRdll.Set_Timing_Start_Delay(self.interrogators[0].opcr_handle, instrDelay, fineDelay)
        ## Slave DAS Interrogator
        # Initialize Clock of slave DAS interrogator
        clockMode = ctypes.c_int(5) # 5 = External Clock 25 MHz deskewed;
        errorCode = errorCode + self.OPCRdll.Initialize_Instrument(self.interrogators[1].opcr_handle, clockMode)
        # Set External Start Mode to level mode
        extStartMode = ctypes.c_int(0)
        errorCode = errorCode + self.OPCRdll.Set_External_Start_Timing_Mode(self.interrogators[1].opcr_handle, extStartMode)
        # Enable external start
        errorCode = errorCode + self.OPCRdll.Enable_External_Start_Timing(self.interrogators[1].opcr_handle)
        # Set Timing Start Delay
        instrDelay = ctypes.c_int(0)
        fineDelay = ctypes.c_int(0) # Add 10ns fine delay
        errorCode = errorCode + self.OPCRdll.Set_Timing_Start_Delay(self.interrogators[1].opcr_handle, instrDelay, fineDelay)
        # Turn on launch EDFA
        errorCode = errorCode + self.OPCRdll.Optical_Output_Amp_On(self.interrogators[1].opcr_handle)
        # Turn on receiver EDFA
        errorCode = errorCode + self.OPCRdll.Optical_Rcvr_Amp_On(self.interrogators[1].opcr_handle)  
        return(errorCode)

    # Set sampling frequency of DAS interrogator    
    def setFs(self, fs):     

        # Single DAS interrogator data acquisition
        if self.mode == 1:
            # Set basic timing parameters with updated pulse repetition rate
            pulsePeriod = ctypes.c_int(floor(10**8/fs))
            pulseWidth = ctypes.c_double(self.pulseWidth/10)
            sampleDelay = ctypes.c_double(0)
            shutterDelay = ctypes.c_double(self.shutterDelay)
            shutterWidth = ctypes.c_double(self.shutterWidth + self.pulseWidth/10)
            errorCode = self.OPCRdll.Set_Timing_CRI4200(self.interrogators[0].opcr_handle, pulsePeriod, pulseWidth, sampleDelay, shutterWidth, shutterDelay)

        # Dual DAS interrogator data acquisition
        elif self.mode == 2:
            # Set basic timing parameters with updated pulse repetition rate
            pulsePeriod = ctypes.c_int(floor(10**8/fs))
            pulseWidth = ctypes.c_double(self.pulseWidth/10)
            sampleDelay = ctypes.c_double(0)
            shutterDelay = ctypes.c_double(self.shutterDelay)
            shutterWidth = ctypes.c_double(self.shutterWidth + self.pulseWidth/10)
            errorCode = self.OPCRdll.Stop_Timing(self.interrogators[0].opcr_handle)
            errorCode = errorCode + self.OPCRdll.Set_Timing_CRI4200(self.interrogators[0].opcr_handle, pulsePeriod, pulseWidth, sampleDelay, shutterWidth, shutterDelay)
            errorCode = errorCode + self.OPCRdll.Set_Timing_CRI4200(self.interrogators[1].opcr_handle, pulsePeriod, pulseWidth, sampleDelay, shutterWidth, shutterDelay)
            errorCode = errorCode + self.OPCRdll.Start_Timing(self.interrogators[0].opcr_handle)

        if errorCode != 0:
                print('Error: Could not set pulse repetition rate of DAS interrogators')
                return(3)
        else:
            print('Pulse Repetition Rate:', 10**8/pulsePeriod.value, 'Hz')
            self.fs = fs
            return(0) 

    # Set pulse width of DAS interrogators   
    def setPulseWidth(self, pulseWidth):     

        # Single DAS interrogator data acquisition
        if self.mode == 1:
            # Set basic timing parameters with updated pulse repetition rate
            pulsePeriod = ctypes.c_int(floor(10**8/self.fs))
            pulseWidth = ctypes.c_double(pulseWidth/10)
            sampleDelay = ctypes.c_double(0)
            shutterDelay = ctypes.c_double(self.shutterDelay)
            shutterWidth = ctypes.c_double(self.shutterWidth + pulseWidth.value)
            errorCode = self.OPCRdll.Set_Timing_CRI4200(self.interrogators[0].opcr_handle, pulsePeriod, pulseWidth, sampleDelay, shutterWidth, shutterDelay)

        # Dual DAS interrogator data acquisition
        elif self.mode == 2:
            # Set basic timing parameters with updated pulse repetition rate
            pulsePeriod = ctypes.c_int(floor(10**8/self.fs))
            pulseWidth = ctypes.c_double(pulseWidth/10)
            sampleDelay = ctypes.c_double(0)
            shutterDelay = ctypes.c_double(self.shutterDelay)
            shutterWidth = ctypes.c_double(self.shutterWidth + pulseWidth.value)
            errorCode = self.OPCRdll.Stop_Timing(self.interrogators[0].opcr_handle)
            errorCode = errorCode + self.OPCRdll.Set_Timing_CRI4200(self.interrogators[0].opcr_handle, pulsePeriod, pulseWidth, sampleDelay, shutterWidth, shutterDelay)
            errorCode = errorCode + self.OPCRdll.Set_Timing_CRI4200(self.interrogators[1].opcr_handle, pulsePeriod, pulseWidth, sampleDelay, shutterWidth, shutterDelay)
            errorCode = errorCode + self.OPCRdll.Start_Timing(self.interrogators[0].opcr_handle)

        if errorCode != 0:
                print('Error: Could not set pulse repetition rate of DAS interrogators')
                return(3)
        else:
            print('Pulse Repetition Rate:', 10**8/pulsePeriod.value, 'Hz')
            self.pulseWidth = 10*pulseWidth.value
            return(0) 

    # Destructor
    def __del__(self):
        print('\n\n')
        del self.interrogators[:]
        print('\n\n')


    # Child Class holding properties of DAS interrogator
    class interrogator:

        # Name of DAS interrogator
        name = ''
        # Interrogator handles
        opcr_handle = None 
        # Status of DAS interrogator
        # 0: Ready
        # 1: DAS interrogator not found
        # 2: Clock could not be initialized
        # 3: Optical pulse repetition rate could not be set
        # 4: Optical pulse width could not be set
        # 5: Gauge length could not be set
        # 6: Launch EDFA current could not be set
        # 7: Receive EDFA current could not be set
        status = 0  
        # Clock Mode
        # 0: Internal Clock 100 MHz (Default)
        # 1: Internal Clock 10 MHz
        # 2: External Clock 25 MHz (from Digitizer)
        # 3: External Clock 10 MHz (from GPS Module)
        clockMode = 0
        # Gauge length in meters
        gaugeLength = 5 # Default is 5 m
        # Launch EDFA current in mA
        launchEDFAcurrent = 250 # Default is 250 mA
        # Receive EDFA current in mA
        recEDFAcurrent = 100 # Default is 100 mA
        # Laser ITU Band Pair
        laserITU = [0,0]
        # Digitizer Board Number (By default, the Master DAS interrogator is connected to board 0)
        boardNum = 0

        # Constructor
        def __init__(self, name, boardNum):

            # Get DAS interrogator name
            self.name = name
            print("Found interrogator: ", self.name)
            # Assign digitizer board number
            self.boardNum = boardNum
            # Load opcr.dll
            self.OPCRdll = ctypes.WinDLL('opcr.dll')
            errorCode = ctypes.c_int(5)
            # Open Communication
            self.opcr_handle = ctypes.c_void_p()
            unique_ID = ctypes.create_string_buffer(256)
            unique_ID.value = str.encode(self.name)
            errorCode = self.OPCRdll.Open_Communication(ctypes.byref(self.opcr_handle), ctypes.byref(unique_ID))
            if errorCode != 0:
                print('Error: Could not establish communication with DAS interrogator ', self.name)
                exit()
            # Get Laser ITU Channels
            self.laserITU[0] = self.getLaserITU(0)
            self.laserITU[1] = self.getLaserITU(1)
            print('Laser ITU Channel Pair: ' + str(self.laserITU[0]) + '/' + str(self.laserITU[1]))
            # Initialize Clock of DAS interrogator
            self.status = self.setClockMode(self.clockMode) # Set interrogator clock mode
            # Set gauge length of DAS interrogator
            self.status = self.setGaugeLength(self.gaugeLength)
            # Initialize launch EDFA
            self.status = self.setLaunchEDFA(self.launchEDFAcurrent)
            # Initialize receive EDFA
            self.status = self.setRecEDFA(self.recEDFAcurrent)
            # Turn on launch EDFA
            errorCode = self.OPCRdll.Optical_Output_Amp_On(self.opcr_handle)
            # Turn on receiver EDFA
            errorCode = self.OPCRdll.Optical_Rcvr_Amp_On(self.opcr_handle)  

        # Get Laser ITU channel
        def getLaserITU(self, laserNum):
            opcr_laserNum = ctypes.c_int(laserNum+1)
            opcr_laserITU = ctypes.c_int(0)
            self.OPCRdll.Get_Laser_ITU(self.opcr_handle, opcr_laserNum, ctypes.byref(opcr_laserITU))
            return(opcr_laserITU.value)

        # Set Clock Mode of DAS interrogator
        def setClockMode(self, clockMode):
            if clockMode == 0:
                print('DAS Clock Mode: 100 MHz DAS Interrogator Clock')
                opcr_clockMode = ctypes.c_int(0)
                opcr_clk1Out = ctypes.c_int(7)
                self.clockMode = 0
            elif clockMode == 1:
                print('DAS Clock Mode: 10 MHz DAS Interrogator Clock')
                opcr_clockMode = ctypes.c_int(0)
                opcr_clk1Out = ctypes.c_int(3)
                self.clockMode = 1
            elif clockMode == 2:
                print('DAS Clock Mode: 25 MHz External Clock')
                opcr_clockMode = ctypes.c_int(2)
                opcr_clk1Out = ctypes.c_int(0)
                self.clockMode = 2
            elif clockMode == 3:
                print('DAS Clock Mode: 10 MHz External Clock')
                opcr_clockMode = ctypes.c_int(1)
                opcr_clk1Out = ctypes.c_int(7)
                self.clockMode = 3
            errorCode = self.OPCRdll.Initialize_Instrument(self.opcr_handle, opcr_clockMode)
            errorCode = errorCode + self.OPCRdll.Set_Reference_Clock(self.opcr_handle, opcr_clk1Out)
            # Change External Start Mode to edge mode
            extStartMode = ctypes.c_int(1)
            errorCode = errorCode + self.OPCRdll.Set_External_Start_Timing_Mode(self.opcr_handle, extStartMode)
            if errorCode != 0:
                print('Error: Could not initialize clock of DAS interrogator ' + self.name)
                return(2)
            else:
                return(0)


        # Set gauge length of DAS interrogator
        def setGaugeLength(self, gaugeLength):
            if gaugeLength == 5:
                gaugeSelected = ctypes.c_int(0)
            elif gaugeLength == 15:
                gaugeSelected = ctypes.c_int(1)
            elif gaugeLength == 25:
                gaugeSelected = ctypes.c_int(2)
            elif gaugeLength == 40:
                gaugeSelected = ctypes.c_int(3)
            else:
                print('Error: Invalid gauge length selected')
                return(5)
            errorCode = self.OPCRdll.Set_Optical_Delay_Coil(self.opcr_handle, gaugeSelected)
            if errorCode != 0:
                print('Error: Could not set gauge length of DAS interrogator ' + self.name)
                return(5)
            else:
                self.gaugeLength = gaugeLength
                print('Gauge length:', gaugeLength, 'm')
                return(0)

        # Set launch EDFA current        
        def setLaunchEDFA(self, launchEDFAcurrent):
                opcr_launchEDFAcurr = ctypes.c_int(launchEDFAcurrent)
                errorCode = self.OPCRdll.Set_Optical_Output_Amp_Current(self.opcr_handle, opcr_launchEDFAcurr)
                if errorCode != 0:
                    print('Error: Could not set launch EDFA current of DAS interrogator ' + self.name)
                    return(6)
                else:
                    self.launchEDFAcurrent = launchEDFAcurrent
                    print('Launch EDFA Current:', launchEDFAcurrent, 'mA')
                    return(0)

        # Set Receiver EDFA current
        def setRecEDFA(self, recEDFAcurrent):
            opcr_recEDFAcurr = ctypes.c_int(recEDFAcurrent)
            errorCode = self.OPCRdll.Set_Optical_Rcvr_Amp_Current(self.opcr_handle, opcr_recEDFAcurr)
            if errorCode != 0:
                print('Error: Could not set receiver EDFA current of DAS interrogator  ' + self.name)
                return(7)
            else:
                self.recEDFAcurrent = recEDFAcurrent
                print('Receiver EDFA Current:', recEDFAcurrent, 'mA')
                return(0)

        # Enable Dither
        def enableDither(self, amp, freq):
            dither_amp = ctypes.c_double(amp)
            dither_freq = ctypes.c_int(floor(100000/freq))
            self.OPCRdll.Enable_Optical_Rcvr_Dither(self.opcr_handle, dither_amp, dither_freq)

        # Disable Dither
        def disableDither(self):
            self.OPCRdll.Disable_Optical_Rcvr_Dither(self.opcr_handle)

        # Destructor
        def __del__(self):
            # Turn off receive EDFA
            self.OPCRdll.Optical_Rcvr_Amp_Off(self.opcr_handle)
            # Turn off launch EDFA
            self.OPCRdll.Optical_Output_Amp_Off(self.opcr_handle)
            # Stop pulsing of DAS interrogator
            self.OPCRdll.Stop_Timing(self.opcr_handle)
            # Close communication with DAS interrogator
            self.OPCRdll.Close_Communication(self.opcr_handle)
            print('Closing communication with DAS interrogator ' + self.name)
            
            
            
            