#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Class for telemetry parameter settings

TMParameter -- describes parameter callback progression
"""

import IMIB
import os
from subprocess import Popen
from blessings import Terminal

class TMParameter():
    
    __paramView = None
    __notifyParameterListStatic = []
    __PIPE_PATH_Param = None
    __paramTerm = Terminal()
    
    def __init__(self, param):
        
        self.__parameter = param
        self.__paramIF = None
        self.__viewKey = None
        
    def getParameterFromServer(self, paramMngr):
        
        self.__paramIF = paramMngr.getParameter(self.__parameter, self.__paramView)
    
    def registerParameter(self):
    
        # arg2: notify on every update, arg3: notify if selected value (raw, default,...) changes (IMIB.PARAM_OOL interesting), arg4: notify only once 
        # arg3: IMIB.PARAM_RAW_VALUE (IMIB.ParamValueType)       
        self.__viewKey = self.__paramIF.registerParam(self.__paramView, True, False, False)
        
        paramInit = self.__paramIF.registerParamInit(self.__paramView, True, False, False)
        with open(self.__PIPE_PATH_Param, 'w') as paramTerminal:           
                paramTerminal.write(str(paramInit)) 
    
    def unregisterParamView(self):       
        self.__paramIF.unregisterView(self.__viewKey)
    
    @classmethod    
    def setParamView(cls, paramView):
        cls.__paramView = paramView

    @classmethod        
    def getParameterNotification(cls, key, value):
        cls.__notifyParameterListStatic.append((key, value))      

        with open(cls.__PIPE_PATH_Param, 'w') as paramTerminal:
            paramTerminal.write(str(key) + ': ' + str(value)) 
        
    @classmethod
    def createParamNotificationTerminal(cls):
        
        cls.__PIPE_PATH_Param = '/tmp/paramNotifyPipe'  
        
        if os.path.exists(cls.__PIPE_PATH_Param):
            os.remove(cls.__PIPE_PATH_Param)
         
        # named pipe            
        os.mkfifo(cls.__PIPE_PATH_Param)
            
        # new terminal subprocess ('xterm' also possible) 
        Popen(['gnome-terminal', '-e', 'tail -f %s' % cls.__PIPE_PATH_Param])   
               
        with open(cls.__PIPE_PATH_Param, 'w') as paramTerminal:
            paramTerminal.write('\n' +  cls.__paramTerm.bold('Waiting for TM parameter...') + '\n')        