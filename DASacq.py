# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 13:01:01 2017

@author: H131339
"""


import GUI
import tkinter as tk

class DASacq:
   
    # Class member containing GUI elements
    window = None
    
    
    def __init__(self):
        
        # Init GUI
        print("\n\nInitializing GUI ...")
        root = tk.Tk()
        self.window = GUI.GUI(master=root)
    
        
        
    

DASacqObj = DASacq()
DASacqObj.window.mainloop()
