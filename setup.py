# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 14:36:10 2017

@author: H131339
"""

import sys
import os
from cx_Freeze import setup, Executable


base = 'Win32GUI' if sys.platform == 'win32' else None

includes = ["matplotlib.backends.backend_tkagg", "matplotlib.backends.backend_qt5agg", "numpy"]
include_files = [r"C:\Users\h131339\AppData\Local\Continuum\Anaconda3\DLLs\tcl86t.dll",
                 r"C:\Users\h131339\AppData\Local\Continuum\Anaconda3\DLLs\tk86t.dll",
                 r"H:\DAS Acq\Python\DASacq\HAL_icon.ico",
                 r"H:\DAS Acq\Python\DASacq\okFrontPanel.dll",
                 r"H:\DAS Acq\Python\DASacq\opcr.dll",
                 r"H:\DAS Acq\Python\DASacq\Alazar\atsapi\atsapi.py"]
packages = ["numpy"]

build_exe_options = {"includes": includes,
                     "include_files": include_files,
                     "packages": packages}

executables = [Executable('DASacq.py', base=base)]

os.environ['TCL_LIBRARY'] = r'C:\Users\h131339\AppData\Local\Continuum\Anaconda3\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\h131339\AppData\Local\Continuum\Anaconda3\tcl\tk8.6'

setup(name='DAS_Interrogator_analyzer',
      version='0.1',
      description='Halliburton DAS Interrogator Analysis Tool',
      options={"build_exe": build_exe_options},
      executables=executables
      )


