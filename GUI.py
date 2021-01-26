# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 15:23:58 2017

@author: H131339
"""



# Class that creates main GUI

import os
import sys
import tkinter as tk
from tkinter import ttk as ttk
from tkinter import messagebox
from tkinter import font
from tkinter import filedialog
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
from math import floor
from datetime import datetime

# Add directories containing Misc scripts and Alazar specific scripts
sys.path.append(os.path.join(os.path.dirname(__file__), 'Alazar'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'Misc'))

import digitizer
import interrogator
import time
import calibration
import diagnostics
import dataAcq
import misc

class GUI(tk.Frame):
    
    # Interrogator handle
    InterrogatorHandle = None
    # Class member containing digitizer elements
    DigitizerHandle = None
    # Integer holding selected DAS interrogator
    selectedDASinterrogator = None
    # tk.IntVar() variable holding selected trigger option
    selectedTriggerOption = None
    # tk.StringVar() variable holding selected clock mode
    selectedClockMode = None    

       
    ##########################################################################
    # Calibration
    ##########################################################################
    # Class member indicating whether system is calibrated
    # [Amplifier Setup Completed, Fiber End Detection Completed, I/Q Imbalance Correction]
    isCalibrated = [0, 0, 0]
    # Fiber End Channel detection results
    fiberEndChann = 0
    fiberSensingRegions = [] 
    # I/Q Imbalance Correction Results (currently not used)
    Ioffset = [0,0]
    Qoffset = [0,0]
    IQgain = [1,1]
    # Treshold to detect optical activity for EDFA initialization
    thresh_EDFAinit = 0.005
    # Thresholds for fiber sensing region detection
    thresh_sensingRegionGap = 200
    # Threshold for saturated channel ratio computation
    thresh_saturatedChannRatio = 1 #0.02 # 0.2 for passive remote circulator scenario;
    # Handle to pdf file containing plots of calibration results
    calibResultsPdf = None
    
    ##########################################################################
    # Diagnostics
    ##########################################################################   
    class diagnostics:

        # Handle to pdf file containing diagnostics results
        resultsPdf = None

        class acousticNoiseFloor:
            # Default channel ranges for acoustic noise floor test (HAL internal)
            channRange = [[4000, 4500]]
            # Test Duration for acoustic noise floor test
            testDur = 30
            # Frequency Range for noise floor calculation
            freqRange = [4000, 5000]
            # Variable holding acoustic noise floor
            medAcousticNoiseFloor = []
    # Constructor
    def __init__(self, master=None):
                
        # Init Interrogator
        print("\n\nInitializing Interrogators ...")
        self.InterrogatorHandle = interrogator.interrogatorAssembly()
        if not self.InterrogatorHandle.interrogators:
            exit()
        
        # Init Digitizer
        print("\n\nInitializing Digitizers ...")
        self.DigitizerHandle = digitizer.digitizer(1, len(self.InterrogatorHandle.interrogators))
        
        # Initialize Frame
        super().__init__(master)
        # Set the window title
        self.master.title("DAS Data Analysis Tool")
        # Set the window size
        self.master.geometry("580x600")
        # Set default window icon
        self.master.wm_iconbitmap('HAL_icon.ico')

        
        #######################################################################        
        # Tab Settings
        #######################################################################
        notebook = ttk.Notebook(master)
        notebook_settings = ttk.Frame(notebook)
        notebook.add(notebook_settings, text='Settings')
        notebook.pack(expand=1, fill="both")
        
        # Add label for "Digitizer Settings"                      
        label_digitizerSettings = tk.LabelFrame(notebook_settings)
        label_digitizerSettings["text"] = "Digitizer Settings"
        label_digitizerSettings["height"] = 100
        label_digitizerSettings["width"] = 455
        label_digitizerSettings.place(x = 10, y = 10)       
        # Add sub-label for Trigger Options
        label_Trigger = tk.LabelFrame(label_digitizerSettings)
        label_Trigger["text"] = "Trigger"
        label_Trigger["height"] = 50
        label_Trigger["width"] = 100
        label_Trigger.place(x=10, y=5)
        # Add trigger options
        self.selectedTriggerOption = tk.IntVar()
        self.selectedTriggerOption.set(2)
        self.radioButton_TriggerRisingEdge = tk.Radiobutton(label_Trigger)
        self.radioButton_TriggerRisingEdge["text"] = "Rising Edge"
        self.radioButton_TriggerRisingEdge["variable"] = self.selectedTriggerOption
        self.radioButton_TriggerRisingEdge["value"] = 1
        self.radioButton_TriggerRisingEdge["command"] = self.Trigger_Callback
        self.radioButton_TriggerRisingEdge.pack()
        self.radioButton_TriggerFallingEdge = tk.Radiobutton(label_Trigger)
        self.radioButton_TriggerFallingEdge["text"] = "Falling Edge"
        self.radioButton_TriggerFallingEdge["variable"] = self.selectedTriggerOption
        self.radioButton_TriggerFallingEdge["value"] = 2
        self.radioButton_TriggerFallingEdge["command"] = self.Trigger_Callback
        self.radioButton_TriggerFallingEdge.pack()       
        # Add sub-label for Clock Modes
        label_clockMode = tk.LabelFrame(label_digitizerSettings)
        label_clockMode["text"] = "Clock Mode"
        label_clockMode["height"] = 70
        label_clockMode["width"] = 260
        label_clockMode.place(x=120, y=5)
        # Add Clock Modes
        self.selectedClockMode = tk.StringVar()
        choices = ('100 MHz DAS Interrogator Clock', '10 MHz DAS Interrogator Clock', '25 MHz ATS Digitizer Clock', '10 MHz GPS Time-Synchronized Clock')
        self.popupMenu_clockMode = ttk.Combobox(label_clockMode, textvariable=self.selectedClockMode, state='readonly', width=37)
        self.popupMenu_clockMode['values'] = choices
        self.popupMenu_clockMode.current(0)
        self.popupMenu_clockMode.bind('<<ComboboxSelected>>', self.ClockMode_Callback)
        self.popupMenu_clockMode.place(x=7, y=13)
        # Disable ability to change clocking mode when running in dual DAS interrogator data acquisition mode
        if len(self.InterrogatorHandle.interrogators) > 1:
            self.popupMenu_clockMode.configure(state='disabled')

        # Add label for "DAS Interrogator Settings"
        label_interrogatorSettings = tk.LabelFrame(notebook_settings)
        label_interrogatorSettings["text"] = "DAS Interrogator Settings"
        label_interrogatorSettings["height"] = 130
        label_interrogatorSettings["width"] = 455
        label_interrogatorSettings.place(x = 10, y = 120)
        # Add popup menu containing name of DAS interrogators
        textbox_interrogatorName = ttk.Label(label_interrogatorSettings, text= 'DAS Interrogator:')
        textbox_interrogatorName.place(x=10, y=15)
        self.selectedDASinterrogator = tk.StringVar()
        choices = self.InterrogatorHandle.interrogatorNames
        self.popupMenu_DASinterrogator = ttk.Combobox(label_interrogatorSettings, textvariable=self.selectedDASinterrogator, state='readonly', width=14)
        self.popupMenu_DASinterrogator['values'] = choices
        self.popupMenu_DASinterrogator.current(0)
        self.popupMenu_DASinterrogator.bind('<<ComboboxSelected>>', self.DASinterrogator_Callback)
        self.popupMenu_DASinterrogator.place(x= 127, y=15)
        # Add DAS sampling rate setting
        textbox_fsDAS = ttk.Label(label_interrogatorSettings, text= 'Sampling Frequency:')
        textbox_fsDAS.place(x=10, y=40)
        self.selectedFsDAS = tk.StringVar()
        choices = ('40 kHz', '32 kHz', '25 kHz', '20 kHz', '16 kHz', '12.5 kHz', '10 kHz', '8 kHz', '5 kHz', '4 kHz', '3.2 kHz', '2 kHz', '1.6 kHz')
        self.popupMenu_fsDAS = ttk.Combobox(label_interrogatorSettings, textvariable=self.selectedFsDAS, state='readonly', width= 8)
        self.popupMenu_fsDAS['values'] = choices
        self.popupMenu_fsDAS.current(6)
        self.popupMenu_fsDAS.bind('<<ComboboxSelected>>', self.fsDAS_Callback)
        self.popupMenu_fsDAS.place(x=127, y=40)
        # Add DAS Gauge Length Settings
        textbox_gaugeLength = ttk.Label(label_interrogatorSettings, text = 'Gauge Length:')
        textbox_gaugeLength.place(x=10, y=65)
        self.selectedGaugeLength = tk.StringVar()
        choices = ('5 m', '15 m', '25 m', '40 m')
        self.popupMenu_gaugeLength = ttk.Combobox(label_interrogatorSettings, textvariable=self.selectedGaugeLength, state='readonly', width= 6)
        self.popupMenu_gaugeLength['values'] = choices
        self.popupMenu_gaugeLength.current(0)
        self.popupMenu_gaugeLength.bind('<<ComboboxSelected>>', self.gaugeLength_Callback)
        self.popupMenu_gaugeLength.place(x=127, y=65)
        # Add Optical Amplifier Settings
        textbox_launchEDFA = ttk.Label(label_interrogatorSettings, text= 'Output Amplifier (mA):')
        textbox_launchEDFA.place(x = 250, y = 15)
        self.selectedLaunchEDFA = tk.StringVar()
        self.entry_launchEDFA = tk.Entry(label_interrogatorSettings, textvariable=self.selectedLaunchEDFA, width= 8)
        self.selectedLaunchEDFA.set(self.InterrogatorHandle.interrogators[0].launchEDFAcurrent)
        self.entry_launchEDFA.bind('<Return>', self.launchEDFA_Callback)
        self.entry_launchEDFA.bind('<FocusOut>', self.launchEDFA_Callback)
        self.entry_launchEDFA.place(x = 380, y = 15)
        textbox_recEDFA = ttk.Label(label_interrogatorSettings, text= 'Receive Amplifier (mA):')
        textbox_recEDFA.place(x = 250, y = 40)
        self.selectedRecEDFA = tk.StringVar()
        self.entry_recEDFA = tk.Entry(label_interrogatorSettings, textvariable=self.selectedRecEDFA, width= 8)
        self.entry_recEDFA.bind('<Return>', self.recEDFA_Callback)
        self.entry_recEDFA.bind('<FocusOut>', self.recEDFA_Callback)
        self.selectedRecEDFA.set(self.InterrogatorHandle.interrogators[0].recEDFAcurrent)
        self.entry_recEDFA.place(x = 380, y = 40)
        # Add Pulse Width
        textbox_pulseWidth = ttk.Label(label_interrogatorSettings, text= 'Pulse Width:')
        textbox_pulseWidth.place(x = 250, y = 65)
        self.selectedPulseWidth = tk.StringVar()
        choices = ('10 ns', '20 ns')
        self.popupMenu_pulseWidth = ttk.Combobox(label_interrogatorSettings, textvariable=self.selectedPulseWidth, width=6)
        self.popupMenu_pulseWidth['values'] = choices
        self.popupMenu_pulseWidth.current(1)
        self.popupMenu_pulseWidth.bind('<<ComboboxSelected>>', self.pulseWidth_Callback)
        self.popupMenu_pulseWidth.place(x = 380, y = 65)
        #self.textbox_pulseWidth = ttk.Label(label_interrogatorSettings, text= self.InterrogatorHandle.pulseWidth)
        #self.textbox_pulseWidth.place(x = 380, y = 95)

        #######################################################################
        # Add tab for "Diagnostics"
        notebook_systemTest = ttk.Frame(notebook)
        notebook.add(notebook_systemTest, text='Diagnostics')
        notebook.pack(expand=1, fill="both")
        
        # Add label for DAS Interrogator Calibration             
        label_calibration = tk.LabelFrame(notebook_systemTest, padx=10, pady=10)
        label_calibration["text"] = "DAS Interrogator Calibration"
        label_calibration["height"] = 100
        label_calibration["width"] = 455
        label_calibration.grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        # Load cross, checkmark and refresh images
        img = Image.open("crossMark.png")
        img = img.resize((20,20), Image.ANTIALIAS)
        self.img_cross = ImageTk.PhotoImage(img)
        img = Image.open("checkMark.png")
        img = img.resize((20,20), Image.ANTIALIAS)
        self.img_check = ImageTk.PhotoImage(img)
        img = Image.open("refresh.png")
        img = img.resize((20,20), Image.ANTIALIAS)
        self.img_refresh = ImageTk.PhotoImage(img)        
        # Add label for 'Amplifier Setup'
        self.canvas_AmplifierSetup = tk.Canvas(label_calibration, width=20, height = 20)
        self.canvas_AmplifierSetup.grid(row=0, column=0, padx = 10)
        self.canvas_img_amplifierSetup = self.canvas_AmplifierSetup.create_image(0,0, anchor=tk.NW, image=self.img_cross)
        textbox_amplifierSetup = ttk.Label(label_calibration, text= 'Amplifier Setup')
        textbox_amplifierSetup.grid(row=0, column=1, sticky=tk.W)
        # Add label for 'Fiber End Detection'
        self.canvas_fiberEnd = tk.Canvas(label_calibration, width=20, height = 20)
        self.canvas_fiberEnd.grid(row=1, column=0, padx = 10)
        self.canvas_img_fiberEnd = self.canvas_fiberEnd.create_image(0,0, anchor=tk.NW, image=self.img_cross)
        textbox_fiberEnd = ttk.Label(label_calibration, text= 'Fiber End Detection')
        textbox_fiberEnd.grid(row=1, column=1, sticky=tk.W)
        # Add label for 'I/Q Imbalance Correction'
        self.canvas_IQImbalanceCorrection = tk.Canvas(label_calibration, width=20, height = 20)
        self.canvas_IQImbalanceCorrection.grid(row=2, column=0, padx = 10)
        self.canvas_img_IQImbalanceCorrection = self.canvas_IQImbalanceCorrection.create_image(0,0, anchor=tk.NW, image=self.img_cross)
        textbox_IQImbalanceCorrection = ttk.Label(label_calibration, text= 'I/Q Imbalance Correction')
        textbox_IQImbalanceCorrection.grid(row=2, column=1, sticky=tk.W)      
        # Add button for "Start Calibration"
        myFont = font.Font(family='Helvetica', size=12, weight='bold')
        button_startCalibration = tk.Button(label_calibration, text= 'Start Calibration', command=self.startCalibration_Callback, font=myFont)
        button_startCalibration.grid(row=0, column=2, rowspan=3, padx = 30)
        
         # Add label for DAS Interrogator Diagnostics             
        label_diagnostics = tk.LabelFrame(notebook_systemTest, padx=10, pady=10)
        label_diagnostics["text"] = "DAS Interrogator Diagnostics"
        label_diagnostics["height"] = 120
        label_diagnostics["width"] = 455
        label_diagnostics.grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        # Add text box and input field for "Start Channel"
        textbox_acousticNoiseFloor_channelRange = tk.Label(label_diagnostics, text='Channel Range:')
        textbox_acousticNoiseFloor_channelRange.grid(row=0, column=0, padx = 10, pady = 10)
        self.acousticNoiseFloor_channelRange = tk.StringVar()
        self.entry_acousticNoiseFloor_channelRange = tk.Entry(label_diagnostics, textvariable=self.acousticNoiseFloor_channelRange, width= 12)
        self.acousticNoiseFloor_channelRange.set('1-512')
        self.entry_acousticNoiseFloor_channelRange.grid(row=0, column=1, padx =8, pady = 10) 
        # Add button for "Start Diagnostics"
        button_startDiagnostics = tk.Button(label_diagnostics, text= 'Start Diagnostics', command=self.startDiagnostics_Callback, font=myFont)
        button_startDiagnostics.grid(row=0, column=2, rowspan=2, padx = 30)
        # Add sub-label for Test Procedure
        label_testProcedure = tk.LabelFrame(label_diagnostics, text='Test Procedure')
        label_testProcedure.grid(row=2, column=2, columnspan = 1, padx = 10, pady = 10)
        # Add radio buttons to differentiate between HAL and SEAFOM test procedure
        self.selectedDiagnosticsFormat = tk.IntVar()
        self.selectedDiagnosticsFormat.set(1)
        radioButton_HALformat = tk.Radiobutton(label_testProcedure, text='HAL internal', variable= self.selectedDiagnosticsFormat, value=1)
        radioButton_HALformat.grid(row=0, column=0, ipady = 5)
        radiobutton_SEAFOMformat = tk.Radiobutton(label_testProcedure, text='SEAFOM', variable=self.selectedDiagnosticsFormat, value=2)
        radiobutton_SEAFOMformat.grid(row=0, column=1, ipady = 5)


        #######################################################################
        # Add tab for "Data Acquisition"
        notebook_daq = ttk.Frame(notebook)
        notebook.add(notebook_daq, text='Data Acquisition')
        notebook.pack(expand=1, fill="both")

        # Add Start Channel Input Box
        textbox_startChann = ttk.Label(notebook_daq, text= 'Start Channel:')
        textbox_startChann.place(x = 15, y = 20)
        self.daqStartChann = tk.StringVar()
        self.entry_daqStartChann = tk.Entry(notebook_daq, textvariable=self.daqStartChann, width= 8)
        self.daqStartChann.set(1)
        #self.entry_launchEDFA.bind('<Return>', self.launchEDFA_Callback)
        #self.entry_launchEDFA.bind('<FocusOut>', self.launchEDFA_Callback)
        self.entry_daqStartChann.place(x = 140, y = 20)

        # Add End Channel Input Box
        textbox_endChann = ttk.Label(notebook_daq, text= 'End Channel:')
        textbox_endChann.place(x = 15, y = 50)
        self.daqEndChann = tk.StringVar()
        self.entry_daqEndChann = tk.Entry(notebook_daq, textvariable=self.daqEndChann, width= 8)
        self.daqEndChann.set(floor(10**8/self.InterrogatorHandle.fs))
        #self.entry_launchEDFA.bind('<Return>', self.launchEDFA_Callback)
        #self.entry_launchEDFA.bind('<FocusOut>', self.launchEDFA_Callback)
        self.entry_daqEndChann.place(x = 140, y = 50)

        # Add Record Duration Input Box
        textbox_recDur = ttk.Label(notebook_daq, text= 'Record Duration (s):')
        textbox_recDur.place(x = 15, y = 80)
        self.daqRecDur = tk.StringVar()
        self.entry_daqRecDur = tk.Entry(notebook_daq, textvariable=self.daqRecDur, width= 8)
        self.daqRecDur.set(10)
        #self.entry_launchEDFA.bind('<Return>', self.launchEDFA_Callback)
        #self.entry_launchEDFA.bind('<FocusOut>', self.launchEDFA_Callback)
        self.entry_daqRecDur.place(x = 140, y = 80)

        # Add Recording Directory Input Box
        textbox_recDir = ttk.Label(notebook_daq, text= 'Recording Directory:')
        textbox_recDir.place(x = 15, y = 110)
        self.daqRecDir = tk.StringVar()
        self.entry_daqRecDir = tk.Entry(notebook_daq, textvariable=self.daqRecDir, width= 48)
        #self.entry_launchEDFA.bind('<Return>', self.launchEDFA_Callback)
        #self.entry_launchEDFA.bind('<FocusOut>', self.launchEDFA_Callback)
        self.entry_daqRecDir.place(x = 140, y = 110)
        # Add button to choose record directory
        button_chooseRecDir = tk.Button(notebook_daq, text= '...', command=self.chooseRecDir_Callback)
        button_chooseRecDir.place(x = 450, y = 108)
        # Add label for data acquisition mode
        label_daqMode = tk.LabelFrame(notebook_daq, padx=10, pady=10)
        label_daqMode["text"] = "Data Acquisition Mode"
        label_daqMode["height"] = 100
        label_daqMode["width"] = 455
        label_daqMode.place(x = 15, y = 150)
        # Add button to start recording
        self.button_daqStartRec = tk.Button(notebook_daq, text= 'Start Data Acquisition', command=self.daqStartRec_Callback)
        self.button_daqStartRec.place(x = 250, y = 185) # Old: x= 220, y= 150
        # Add radio buttons to choose between immediate or scheduled data acquisition
        self.selectedDaqMode = tk.IntVar()
        self.selectedDaqMode.set(1)
        self.radioButton_daqModeImmediate = tk.Radiobutton(label_daqMode, text='Immediate', variable= self.selectedDaqMode, value=1, state='disabled', command=self.daqMode_Callback)
        self.radioButton_daqModeImmediate.grid(row=0, column=0)
        self.radiobutton_daqModeScheduled = tk.Radiobutton(label_daqMode, text='Scheduled', variable=self.selectedDaqMode, value=2, state='disabled', command=self.daqMode_Callback)
        self.radiobutton_daqModeScheduled.grid(row=1, column=0)
        # Add time picker widget
        currTime = datetime.now()
        self.hourstr=tk.StringVar(self, str(currTime.hour))
        self.hour = tk.Spinbox(label_daqMode,from_=0,to=23,wrap=True,textvariable=self.hourstr,width=2,state="disabled")
        self.minstr=tk.StringVar(self,str(currTime.minute))
        self.minstr.trace("w",self.trace_var)
        self.last_value = ""
        self.min = tk.Spinbox(label_daqMode,from_=0,to=59,wrap=True,textvariable=self.minstr,width=2,state="disabled")
        textbox_blanks = ttk.Label(label_daqMode, text= '     ')
        textbox_blanks.grid(row=1, column = 1)
        self.hour.grid(row=1, column = 2)
        textbox_blanks = ttk.Label(label_daqMode, text= ' : ')
        textbox_blanks.grid(row=1, column = 3)
        self.min.grid(row=1, column = 4)

        #######################################################################     
        # Add text window with scrollbar
        textWindow_canvas = tk.Canvas(master, height = 100, width = 300)
        textWindow_canvas.place(x = 10, y = 320)
        textWindow_text = ttk.Label(textWindow_canvas, text= 'Output Window', justify=tk.LEFT)
        textWindow_text.pack(side=tk.TOP, fill='y')
        self.textWindow = tk.Text(textWindow_canvas, height=10, width=65)
        self.textWindow.pack(side=tk.LEFT, fill='y')
        textWindow_vscrollbar = tk.Scrollbar(textWindow_canvas, command=self.textWindow.yview)
        textWindow_vscrollbar.pack(side=tk.RIGHT, fill='y')
        self.textWindow.config(yscrollcommand=textWindow_vscrollbar.set)
        self.textWindow.insert(tk.END, 'Initializing DAS Interrogator ... done\n')
        self.textWindow.insert(tk.END, 'Initializing Digitizer ... done\n\n')
        # Add progress bar
        self.progressBar = ttk.Progressbar(master, orient = 'horizontal', length=520, mode='determinate')  
        self.progressBar["maximum"] = 1
        self.progressBar.pack()
        self.progressBar.place(x = 10, y = 510)
        # Add buttons
        myFont = font.Font(family='Helvetica', size=11)
        self.quitButton = tk.Button(master, text="Exit", command=self.exit_GUI, font=myFont)
        self.quitButton.place(x=220,y=550)
        
        
    def exit_GUI(self):
        del self.InterrogatorHandle
        del self.DigitizerHandle
        self.master.quit()
        
    def Trigger_Callback(self):

        if self.selectedTriggerOption.get() != self.DigitizerHandle.triggerMode:
            for board in self.DigitizerHandle.boardHandles:
                self.DigitizerHandle.ConfigTrigger(board, self.selectedTriggerOption.get())
            # Rising Edge Trigger
            if self.selectedTriggerOption.get() == 1:
                self.textWindow.insert(tk.END, 'Trigger Mode: Rising Edge\n')
                self.textWindow.see(tk.END)
            # Falling Edge Trigger
            else:
                self.textWindow.insert(tk.END, 'Trigger Mode: Falling Edge\n')
                self.textWindow.see(tk.END)
                       
    def ClockMode_Callback(self, event): 

        if self.popupMenu_clockMode.current() != self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].clockMode:
            self.progressBar["value"] = 0.25
            self.progressBar.update()
            # DAS Interrogator is Master Clock Source
            if self.popupMenu_clockMode.current() == 0 or self.popupMenu_clockMode.current() == 1 or self.popupMenu_clockMode.current() == 3:  
                self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].setClockMode(self.popupMenu_clockMode.current())     
                # Start Timing
                self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].OPCRdll.Start_Timing(self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].opcr_handle)
                # Turn on launch EDFA
                self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].OPCRdll.Optical_Output_Amp_On(self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].opcr_handle)
                # Turn on receiver EDFA
                self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].OPCRdll.Optical_Rcvr_Amp_On(self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].opcr_handle)
                self.progressBar["value"] = 0.75
                self.progressBar.update()
                for board in self.DigitizerHandle.boardHandles:
                    if self.popupMenu_clockMode.current() == 0 or self.popupMenu_clockMode.current() == 3: 
                        self.DigitizerHandle.ConfigClock(board, 0)
                    else:
                        self.DigitizerHandle.ConfigClock(board, 1)
                self.progressBar["value"] = 1
                self.progressBar.update()
                time.sleep(0.2)
                self.progressBar["value"] = 0      
            # ATS Digitizer is Master Clock Source
            elif self.popupMenu_clockMode.current() == 2:
                for board in self.DigitizerHandle.boardHandles:
                    self.DigitizerHandle.ConfigClock(board, self.popupMenu_clockMode.current())
                self.progressBar["value"] = 0.5
                self.progressBar.update()
                time.sleep(10)
                self.progressBar["value"] = 0.75
                self.progressBar.update()
                self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].setClockMode(self.popupMenu_clockMode.current())
                # Start Timing
                self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].OPCRdll.Start_Timing(self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].opcr_handle)
                # Turn on launch EDFA
                self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].OPCRdll.Optical_Output_Amp_On(self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].opcr_handle)
                # Turn on receiver EDFA
                self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].OPCRdll.Optical_Rcvr_Amp_On(self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].opcr_handle)
                self.progressBar["value"] = 1
                self.progressBar.update()
                time.sleep(0.2)
                self.progressBar["value"] = 0

            # For GPS clock enable data acquisition mode selection
            if self.popupMenu_clockMode.current() == 3:
                self.radioButton_daqModeImmediate["state"] = 'normal'
                self.radiobutton_daqModeScheduled["state"] = 'normal'
                self.selectedDaqMode.set(1)
            else:
                self.selectedDaqMode.set(1)
                self.daqMode_Callback()
                self.radioButton_daqModeImmediate["state"] = 'disabled'
                self.radiobutton_daqModeScheduled["state"] = 'disabled'

            self.textWindow.insert(tk.END, 'Clock Mode: ' + self.popupMenu_clockMode.get() + '\n')
            self.textWindow.see(tk.END) 
                            
    def DASinterrogator_Callback(self, event):
        # Update GUI launch EDFA setting
        self.selectedLaunchEDFA.set(self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].launchEDFAcurrent)
        # Update GUI receive EDFA setting
        self.selectedRecEDFA.set(self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].recEDFAcurrent)
        # Update GUI gauge length setting
        choices = [5, 15, 25, 40]
        ind = [x for x in range(len(choices)) if choices[x] == self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].gaugeLength]
        self.popupMenu_gaugeLength.current(ind)
        # Update pulse width setting
        #self.textbox_pulseWidth["text"] = self.InterrogatorHandle.pulseWidth
        self.popupMenu_pulseWidth.current(self.InterrogatorHandle.pulseWidth/10 - 1)
        # Update GUI DAS pulse repetition rate setting
        choices = [40000, 32000, 25000, 20000, 16000, 12500, 10000, 8000, 5000, 4000, 3200]
        ind = [x for x in range(len(choices)) if choices[x] == self.InterrogatorHandle.fs]
        self.popupMenu_fsDAS.current(ind)
         
    def fsDAS_Callback(self, event):
        fsDAS = self.InterrogatorHandle.dict_ts2fs[self.popupMenu_fsDAS.current()][1]
        
        if self.InterrogatorHandle.fs != fsDAS:
            self.progressBar["value"] = 0.25
            self.progressBar.update()
            # Set DAS sampling freuency to 'fsDAS'
            self.InterrogatorHandle.setFs(fsDAS)
            self.progressBar["value"] = 1
            self.progressBar.update()
            time.sleep(0.2)
            self.progressBar["value"] = 0
            self.textWindow.insert(tk.END, 'Sampling Frequency: ' + self.popupMenu_fsDAS.get() + '\n')
            self.textWindow.see(tk.END)
            self.isCalibrated[0] = 0
            self.update()
                        
    def gaugeLength_Callback(self, event):      
        # Map selected pop-up menu entry to gauge length and pulse width
        if self.popupMenu_gaugeLength.current() == 0:
            gaugeLength = 5
            pulseWidth = 20
            pulseWidth_choices = ('10 ns', '20 ns')
        elif self.popupMenu_gaugeLength.current() == 1:
            gaugeLength = 15
            pulseWidth = 70
            pulseWidth_choices = ('10 ns', '20 ns', '30 ns', '40 ns', '50 ns', '60 ns', '70 ns')
        elif self.popupMenu_gaugeLength.current() == 2:
            gaugeLength = 25
            pulseWidth = 100
            pulseWidth_choices = ('10 ns', '20 ns', '30 ns', '40 ns', '50 ns', '60 ns', '70 ns', '80 ns', '90 ns', '100 ns')
        elif self.popupMenu_gaugeLength.current() == 3:
            gaugeLength = 40
            pulseWidth = 100
            pulseWidth_choices = ('10 ns', '20 ns', '30 ns', '40 ns', '50 ns', '60 ns', '70 ns', '80 ns', '90 ns', '100 ns')
        
        if gaugeLength != self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].gaugeLength:
            # Change gauge length and pulse width
            print('Gauge Length: ' + str(gaugeLength) + ' m')
            print('Pulse Width: ' + str(pulseWidth) + ' ns')
            self.progressBar["value"] = 0.25
            self.progressBar.update()
            for i in range(len(self.InterrogatorHandle.interrogators)):
                self.InterrogatorHandle.interrogators[i].setGaugeLength(gaugeLength)
            self.progressBar["value"] = 0.5
            self.progressBar.update()
            self.InterrogatorHandle.setPulseWidth(pulseWidth)         
            # Update pulse width drop-down menu options
            self.popupMenu_pulseWidth['values'] = pulseWidth_choices
            self.popupMenu_pulseWidth.current(len(pulseWidth_choices) - 1)    
            self.progressBar["value"] = 1
            self.progressBar.update()
            time.sleep(0.2)
            self.progressBar["value"] = 0
            #self.textbox_pulseWidth["text"] = self.InterrogatorHandle.pulseWidth
            self.textWindow.insert(tk.END, 'Gauge Length: ' + self.popupMenu_gaugeLength.get() + '\n')
            self.textWindow.insert(tk.END, 'Pulse Width: ' + str(self.InterrogatorHandle.pulseWidth) + ' ns\n')
            self.textWindow.see(tk.END)
            # Reset calibration
            self.isCalibrated[0] = 0
            self.isCalibrated[1] = 0
            self.fiberSensingRegions = []
            self.fiberEndChann = 0
            self.canvas_AmplifierSetup.itemconfig(self.canvas_img_amplifierSetup, image=self.img_cross)
            self.canvas_fiberEnd.itemconfig(self.canvas_img_fiberEnd, image=self.img_cross)
            self.update()

    def pulseWidth_Callback(self, event):
        # Calculate pulse width from selected entry in drop-down menu
        pulseWidth = (self.popupMenu_pulseWidth.current() + 1) * 10
        # Check if selected pulse width is different than current pulse width
        if pulseWidth != self.InterrogatorHandle.pulseWidth:
            # Change pulse width
            print('Pulse Width: ' + str(pulseWidth) + ' ns')
            self.progressBar["value"] = 0.5
            self.progressBar.update()
            self.InterrogatorHandle.setPulseWidth(pulseWidth)
            self.textWindow.insert(tk.END, 'Pulse Width: ' + str(self.InterrogatorHandle.pulseWidth) + ' ns\n')
            self.textWindow.see(tk.END)
            self.progressBar["value"] = 1
            self.progressBar.update()
            # Reset calibration
            self.isCalibrated[0] = 0
            self.isCalibrated[1] = 0
            self.fiberSensingRegions = []
            self.fiberEndChann = 0
            self.canvas_AmplifierSetup.itemconfig(self.canvas_img_amplifierSetup, image=self.img_cross)
            self.canvas_fiberEnd.itemconfig(self.canvas_img_fiberEnd, image=self.img_cross)
            self.update()

    def launchEDFA_Callback(self, event):
        if (int(self.selectedLaunchEDFA.get()) != self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].launchEDFAcurrent):
            self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].setLaunchEDFA(int(self.selectedLaunchEDFA.get()))
            self.textWindow.insert(tk.END, 'Output Amplifier Current: ' + self.selectedLaunchEDFA.get() + 'mA\n')
            self.textWindow.see(tk.END)
            # Reset Calibration
            self.isCalibrated[1] = 0
            self.canvas_AmplifierSetup.itemconfig(self.canvas_img_amplifierSetup, image=self.img_cross)
            self.update()
                             

    def recEDFA_Callback(self, event):
        if (int(self.selectedRecEDFA.get()) != self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].recEDFAcurrent):
            self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].setRecEDFA(int(self.selectedRecEDFA.get()))
            self.textWindow.insert(tk.END, 'Receive Amplifier Current: ' + self.selectedRecEDFA.get() + 'mA\n')
            self.textWindow.see(tk.END)
            # Reset Calibration
            self.isCalibrated[1] = 0
            self.canvas_AmplifierSetup.itemconfig(self.canvas_img_amplifierSetup, image=self.img_cross)
            self.update()
            
    def startCalibration_Callback(self):
        
        self.textWindow.insert(tk.END, '\nStarting Calibration ...\n')
        self.textWindow.insert(tk.END, 'Gauge Length used for Calibration: ' + str(self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].gaugeLength) + 'm\n')
        self.textWindow.see(tk.END)
        # Close all open Matlab figures
        plt.close('all')
        # Open Calibration Report File
        try:
            fileName = os.path.join(os.path.dirname(__file__), 'Docs', 'calibrationReport_' + str(self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].gaugeLength) + 'm.pdf')
            self.calibResultsPdf = PdfPages(fileName)
        except PermissionError:
            messagebox.showerror('Permission Error', 'Please close PDF file of previous calibration run and try again.')
            return        
        
        # Amplifier Setup
        self.canvas_AmplifierSetup.itemconfig(self.canvas_img_amplifierSetup, image=self.img_refresh)
        self.update()
        for interrogator in self.InterrogatorHandle.interrogators:
            calibration.amplifierSetup(self, interrogator)
        # Flag amplifier setup as having completed successfully
        self.isCalibrated[0] = 1
        self.canvas_AmplifierSetup.itemconfig(self.canvas_img_amplifierSetup, image=self.img_check)
        self.update()
        
        # Fiber End Detection
        self.canvas_fiberEnd.itemconfig(self.canvas_img_fiberEnd, image= self.img_refresh)
        self.update()
        calibration.fiberEndDetection(self)
        self.canvas_fiberEnd.itemconfig(self.canvas_img_fiberEnd, image= self.img_check)
        self.update()  

        # I/Q Imbalance Correction
        self.canvas_IQImbalanceCorrection.itemconfig(self.canvas_img_IQImbalanceCorrection, image=self.img_refresh)
        self.update()
        # calibration.IQImbalanceCorrection(self)
        self.canvas_IQImbalanceCorrection.itemconfig(self.canvas_img_IQImbalanceCorrection, image=self.img_check)
        self.update()        
        # Generate page summarizing digitizer and interrogator settings
        if self.DigitizerHandle.triggerMode == 1:
            triggerMode = 'Rising Edge'
        else:
            triggerMode = 'Falling Edge'
        
        if self.DigitizerHandle.clockMode == 0:
            clockMode = '100 MHz DAS Interrogator Clock'
        elif self.DigitizerHandle.clockMode == 1:
            clockMode = '10 MHz DAS Interrogator Clock'
        else:
            clockMode = '25 MHz ATS Digitizer Clock'
        
        axs1 = plt.subplot2grid((10,1),(0,0), rowspan=2)
        axs1.text(0,0,'Digitizer Settings:', style='italic', weight='bold', size='large')
        axs1.invert_yaxis()
        axs1.axis('off')
        digitizer_data = [['Trigger:', triggerMode], ['Clock Mode:', clockMode]]
        axs1.table(cellText=digitizer_data, rowLoc='center', colWidths=[.5,.5], colLoc='center', loc='center', bbox=[0,0.4, 1, 0.5])
        axs2 = plt.subplot2grid((10,1),(2,0), rowspan=4)
        axs2.text(0,0,'Interrogator Settings:', style='italic', weight='bold', size='large')
        axs2.invert_yaxis()
        axs2.axis('off')
        interrogatorNames = ''
        launchEDFAcurrent = ''
        recEDFAcurrent = ''
        for interrogator in self.InterrogatorHandle.interrogators:
            interrogatorNames = interrogatorNames + interrogator.name + ' / '
            launchEDFAcurrent = launchEDFAcurrent + str(interrogator.launchEDFAcurrent) + ' mA / '
            recEDFAcurrent = recEDFAcurrent + str(interrogator.recEDFAcurrent) + ' mA / '
        
        interrogator_data = [['DAS Interrogator:', interrogatorNames[0:-3]], 
                             ['Sampling Frequency:', str(self.InterrogatorHandle.fs / 1000) + ' kHz'], 
                             ['Gauge Length:', str(self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].gaugeLength) + ' m'],
                             ['Pulse Width:', str(self.InterrogatorHandle.pulseWidth) + ' ns'],
                             ['Output Amplifier Current:', launchEDFAcurrent[0:-3]],
                             ['Receive Amplifier Current:', recEDFAcurrent[0:-3]]]
        axs2.table(cellText=interrogator_data, rowLoc='center', colWidths=[.5,.5], colLoc='center', loc='center', bbox=[0,0.2, 1, 0.75])
        axs3 = plt.subplot2grid((10,1),(6,0), rowspan=4)
        axs3.text(0,0,'Calibration Results:', style='italic', weight='bold', size='large')
        axs3.invert_yaxis()
        axs3.axis('off')
        calibration_results = [['Fiber Sensing Region:', str(self.fiberSensingRegions[0][0]) + ' - ' + str(self.fiberSensingRegions[-1][1])],
                               ['Fiber End Channel (Fine):', str(self.fiberEndChann)]]
        #                        ['I Offset (Laser 1 / Laser 2):', str(self.Ioffset[0]) + ' / ' + str(self.Ioffset[1])],
        #                        ['Q Offset (Laser 1 / Laser 2):', str(self.Qoffset[0]) + ' / ' + str(self.Qoffset[1])],
        #                        ['I/Q Gain (Laser 1 / Laser 2):', str(self.IQgain[0]) + ' / ' + str(self.IQgain[1])]]
        axs3.table(cellText=calibration_results,  rowLoc='center', colWidths=[.5,.5], colLoc='center', loc='center', bbox=[0,0.33, 1, 0.62])

        self.calibResultsPdf.savefig()
        plt.close()
        
        self.progressBar["value"] = 0
        self.progressBar.update()
        
        self.calibResultsPdf.close()
        result = messagebox.askyesno("Calibration Report", "Calibration complete. Do you want to open the report?")
        if result == True:
            os.startfile(fileName)
        
        
    def startDiagnostics_Callback(self):

        # Extract channel range for DAS noise floor calculation
        channRangeStr = self.acousticNoiseFloor_channelRange.get()
        [startChann, endChann, errorCode] = misc.getRangefromStr(channRangeStr)
        if errorCode != 0:
            messagebox.showerror('Channel Range Error', 'Invalid channel range.')
            self.acousticNoiseFloor_channelRange.set('1-512')
        # Make user-supplied channel range compliant with channel range supported by ATS-9440 digitizer
        [startChann, endChann] = dataAcq.getChannRange(startChann,endChann)
        # Use user-defined channel range for DAS noise floor calculation
        self.diagnostics.acousticNoiseFloor.channRange[0][0] = startChann
        self.diagnostics.acousticNoiseFloor.channRange[0][1] = endChann
        # Update channel range input field
        self.acousticNoiseFloor_channelRange.set(str(startChann) + '-' + str(endChann))
        # Set correct frequency range for noise floor calculation
        endFreq = int(max(500, self.InterrogatorHandle.fs / 2 - 500))
        startFreq = int(max(200, endFreq - 1000))
        self.diagnostics.acousticNoiseFloor.freqRange = [startFreq, endFreq]
        # Display parameters used for noise floor calculation
        self.textWindow.insert(tk.END, '\nStarting DAS Interrogator Diagnostics ...\n')
        self.textWindow.insert(tk.END, 'Gauge Length: ' + str(self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].gaugeLength) + ' m\n')
        self.textWindow.insert(tk.END, 'Pulse Width: ' + str(self.InterrogatorHandle.pulseWidth) + ' ns\n')
        self.textWindow.insert(tk.END, 'Channel Range: ' + str(self.diagnostics.acousticNoiseFloor.channRange[0][0]) + ' - ' + str(self.diagnostics.acousticNoiseFloor.channRange[0][1]) + '\n')
        self.textWindow.insert(tk.END, 'Frequency Range: ' + str(self.diagnostics.acousticNoiseFloor.freqRange[0]) + ' Hz - ' + str(self.diagnostics.acousticNoiseFloor.freqRange[1]) + ' Hz\n')
        self.textWindow.see(tk.END)
        self.progressBar["value"] = 0
        self.progressBar.update()
        # Close all open Matlab figures
        plt.close('all')
        # Open Diagnostics Report File
        try:
            fileName = os.path.join(os.path.dirname(__file__), 'Docs', 'diagnosticsReport_' + str(self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].gaugeLength) + 'm.pdf')
            self.diagnostics.resultsPdf = PdfPages(fileName)
        except PermissionError:
            messagebox.showerror('Permission Error', 'Please close PDF file of previous diagnostics run and try again.')
            return
        # Acoustic Noise Floor Test
        self.diagnostics.acousticNoiseFloor.medAcousticNoiseFloor = diagnostics.AcousticNoiseFloorTest(self)
        
        # Add page summarizing Acoustic Noise Floor Results
        if self.DigitizerHandle.triggerMode == 1:
            triggerMode = 'Rising Edge'
        else:
            triggerMode = 'Falling Edge'
         
        if self.DigitizerHandle.clockMode == 0:
            clockMode = '100 MHz DAS Interrogator Clock'
        elif self.DigitizerHandle.clockMode == 1:
            clockMode = '10 MHz DAS Interrogator Clock'
        else:
            clockMode = '25 MHz ATS Digitizer Clock'
        axs1 = plt.subplot2grid((10,1),(0,0), rowspan=2)
        axs1.text(0,0,'Digitizer Settings:', style='italic', weight='bold', size='large')
        axs1.invert_yaxis()
        axs1.axis('off')
        digitizer_data = [['Trigger:', triggerMode], ['Clock Mode:', clockMode]]
        axs1.table(cellText=digitizer_data, rowLoc='center', colWidths=[.5,.5], colLoc='center', loc='center', bbox=[0,0.4, 1, 0.5])
        axs2 = plt.subplot2grid((10,1),(2,0), rowspan=4)
        axs2.text(0,0,'Interrogator Settings:', style='italic', weight='bold', size='large')
        axs2.invert_yaxis()
        axs2.axis('off')
        interrogatorNames = ''
        launchEDFAcurrent = ''
        recEDFAcurrent = ''
        for interrogator in self.InterrogatorHandle.interrogators:
            interrogatorNames = interrogatorNames + interrogator.name + ' / '
            launchEDFAcurrent = launchEDFAcurrent + str(interrogator.launchEDFAcurrent) + ' mA / '
            recEDFAcurrent = recEDFAcurrent + str(interrogator.recEDFAcurrent) + ' mA / '
        interrogator_data = [['DAS Interrogator:', interrogatorNames[0:-3]], 
                             ['Sampling Frequency:', str(self.InterrogatorHandle.fs / 1000) + ' kHz'], 
                             ['Gauge Length:', str(self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].gaugeLength) + ' m'],
                             ['Pulse Width:', str(self.InterrogatorHandle.pulseWidth) + ' ns'],
                             ['Output Amplifier Current:', launchEDFAcurrent[0:-3]],
                             ['Receive Amplifier Current:', recEDFAcurrent[0:-3]]]
        axs2.table(cellText=interrogator_data, rowLoc='center', colWidths=[.5,.5], colLoc='center', loc='center', bbox=[0,0.2, 1, 0.75])
        axs3 = plt.subplot2grid((10,1),(6,0), rowspan=4)
        axs3.text(0,0,'Acoustic Noise Floor Results:', style='italic', weight='bold', size='large')
        axs3.invert_yaxis()
        axs3.axis('off')
 
        if len(self.diagnostics.acousticNoiseFloor.medAcousticNoiseFloor) == 3: # Single DAS interrogator acquisition
            diagnostics_results = [['Frequency Range:', str(self.diagnostics.acousticNoiseFloor.freqRange[0]) + ' Hz - ' + str(self.diagnostics.acousticNoiseFloor.freqRange[1]) + ' Hz'],
                                   ['Channel Range:', str(self.diagnostics.acousticNoiseFloor.channRange[0][0]) + ':' + str(self.diagnostics.acousticNoiseFloor.channRange[0][1])],
                                   ['Acoustic Noise Floor - Laser 1:', '{0:.2f} dB'.format(self.diagnostics.acousticNoiseFloor.medAcousticNoiseFloor[0])],
                                   ['Acoustic Noise Floor - Laser 2:', '{0:.2f} dB'.format(self.diagnostics.acousticNoiseFloor.medAcousticNoiseFloor[1])],
                                   ['Acoustic Noise Floor - Laser 1+2:', '{0:.2f} dB'.format(self.diagnostics.acousticNoiseFloor.medAcousticNoiseFloor[2])]]
        else: # Dual DAS interrogator acquisition
            acousticNoiseFloorString_interrogator1 = '{0:.2f} dB'.format(self.diagnostics.acousticNoiseFloor.medAcousticNoiseFloor[0]) + ' / ' + '{0:.2f} dB'.format(self.diagnostics.acousticNoiseFloor.medAcousticNoiseFloor[1]) + ' / ' + '{0:.2f} dB'.format(self.diagnostics.acousticNoiseFloor.medAcousticNoiseFloor[4])
            acousticNoiseFloorString_interrogator2 = '{0:.2f} dB'.format(self.diagnostics.acousticNoiseFloor.medAcousticNoiseFloor[2]) + ' / ' + '{0:.2f} dB'.format(self.diagnostics.acousticNoiseFloor.medAcousticNoiseFloor[3]) + ' / ' + '{0:.2f} dB'.format(self.diagnostics.acousticNoiseFloor.medAcousticNoiseFloor[5])
            diagnostics_results = [['Frequency Range:', str(self.diagnostics.acousticNoiseFloor.freqRange[0]) + ' Hz - ' + str(self.diagnostics.acousticNoiseFloor.freqRange[1]) + ' Hz'],
                                   ['Channel Range:', str(self.diagnostics.acousticNoiseFloor.channRange[0][0]) + ':' + str(self.diagnostics.acousticNoiseFloor.channRange[0][1])],
                                   [self.InterrogatorHandle.interrogators[0].name + ' - Acoustic Noise Floor (Laser 1/2/1&2):', acousticNoiseFloorString_interrogator1],
                                    [self.InterrogatorHandle.interrogators[1].name + ' - Acoustic Noise Floor (Laser 1/2/1&2):', acousticNoiseFloorString_interrogator2],
                                   ['Acoustic Noise Floor - Laser 1-4:', '{0:.2f} dB'.format(self.diagnostics.acousticNoiseFloor.medAcousticNoiseFloor[6])]]
        axs3.table(cellText=diagnostics_results,  rowLoc='center', colWidths=[.5,.5], colLoc='center', loc='center', bbox=[0,0.33, 1, 0.62])

        self.diagnostics.resultsPdf.savefig()
        self.progressBar["value"] = 0
        self.progressBar.update()
        self.update()
        self.diagnostics.resultsPdf.close()
        result = messagebox.askyesno("Diagnostics Report", "Diagnostics complete. Do you want to open the report?")
        if result == True:
            os.startfile(fileName)

    def chooseRecDir_Callback(self):
        # Open dialog box to choose recording directory
        self.daqRecDir.set(filedialog.askdirectory())

    def daqStartRec_Callback(self):
        self.button_daqStartRec["state"] = "disabled"
        # Check if recording directory is populated
        if not self.daqRecDir.get():
            messagebox.showerror('Error', 'No Recording Directory selected')
        else:
            # Check if clock mode is external GPS clock
            if self.popupMenu_clockMode.current() == 3:
                # Immediate Data Acquisition Mode
                if self.selectedDaqMode.get() == 1:
                    # Disable external start
                    self.InterrogatorHandle.OPCRdll.Disable_External_Start_Timing(self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].opcr_handle)
                    # Stop DAS Interrogator Pulsing (takes approx. 0.55 secs)
                    self.InterrogatorHandle.OPCRdll.Stop_Timing(self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].opcr_handle)
                    # Enable external start (takes approx. 0.17 secs)
                    print("Arming DAS Interrogator")
                    self.InterrogatorHandle.OPCRdll.Enable_External_Start_Timing(self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].opcr_handle)
                # Scheduled Data Acquisition Mode
                else:
                    # Check that the scheduled time is at least 2 seconds in the future
                    scheduledTime_secs = int(self.hour.get())*60*60 + int(self.min.get())*60
                    currTime = datetime.now()
                    currTime_secs = currTime.hour*60*60 + currTime.minute*60 + currTime.second
                    print('\n\n')
                    if scheduledTime_secs - currTime_secs >= 2:
                        # Disable external start
                        self.InterrogatorHandle.OPCRdll.Disable_External_Start_Timing(self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].opcr_handle)                       
                        # Stop DAS Interrogator Pulsing (takes approx. 0.55 secs)
                        self.InterrogatorHandle.OPCRdll.Stop_Timing(self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].opcr_handle)                       
                        # Update current time
                        currTime = datetime.now()
                        currTime_secs = currTime.hour*60*60 + currTime.minute*60 + currTime.second
                        # Wait until we are within 1 second of scheduled recording start time
                        while scheduledTime_secs - currTime_secs > 1:
                            time.sleep(0.1) # Sleep 100 milliseconds
                            currTimeOld = currTime_secs
                            currTime = datetime.now()
                            currTime_secs = currTime.hour*60*60 + currTime.minute*60 + currTime.second
                            if currTimeOld != currTime_secs:
                                print('Commencing data acquisition in ' + str(scheduledTime_secs - currTime_secs) + ' secs') 
                        # Enable external start (takes approx. 0.17 secs)
                        print("Arming DAS Interrogator")
                        self.InterrogatorHandle.OPCRdll.Enable_External_Start_Timing(self.InterrogatorHandle.interrogators[self.popupMenu_DASinterrogator.current()].opcr_handle)
                    else:
                        messagebox.showerror('Error', 'Scheduled Data Acquisition Start Time Invalid')
                        self.button_daqStartRec["state"] = "normal"
                        return

            for interrogator in self.InterrogatorHandle.interrogators:
                interrogator.enableDither(2, 10)
            dataAcq.storeDataToDisk(self, int(self.daqStartChann.get()), int(self.daqEndChann.get()), int(self.daqRecDur.get()), 3)
            for interrogator in self.InterrogatorHandle.interrogators:
                interrogator.disableDither()
                
            
        self.button_daqStartRec["state"] = "normal"

    def trace_var(self,*args):
        if self.last_value == "59" and self.minstr.get() == "0":
            self.hourstr.set(int(self.hourstr.get())+1 if self.hourstr.get() !="23" else 0)
        self.last_value = self.minstr.get()

    def daqMode_Callback(self):

        if self.selectedDaqMode.get() == 1: # Immediate Data Acquisition Mode
            self.hour["state"] = "disabled"
            self.min["state"] = "disabled"
        else: # Scheduled Data Acquisition Mode
            currTime = datetime.now()
            self.hourstr.set(currTime.hour)
            self.minstr.set(currTime.minute)
            self.hour["state"] = "readonly"
            self.min["state"] = "readonly"



