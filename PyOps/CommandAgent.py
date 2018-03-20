#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Command Injection services
Access to SCOS-2000 commanding system

"""

from BaseAgent import BaseAgent
from ViewInterfaces import CommandInjectMngrView
import IBASE, ITC, ITC_INJ

from colorama import Fore, Back, Style

class CommandAgent(BaseAgent):
        
    def __init__(self):
        self.__namingService = 'TC_INJ_002'
        self.__serverMngrType = ITC_INJ.TCinjectServerMngr
        self.__cmdInjMngrView = None
        self._cmdInjMngr = None
        self.__cmdView = CommandInjectMngrView()
        self.__poaIdStr = 'CmdInjectionObjectId' 
                      
        BaseAgent.__init__(self)
        
    def getNamingService(self):
        return self.__namingService   
     
    def getServerMngrType(self):
        return self.__serverMngrType
    
    def createCmdInjMngrView(self):
        self.__cmdInjMngrView = self.createCorbaObject(self.__cmdView,self.__poaIdStr)
        
    def getCmdInjMngrView(self):
        return self.__cmdInjMngrView
    
    def tcInjectMngr(self):
        self._cmdInjMngr = self._serverMngr.getTCinjectMngr(self.__cmdInjMngrView, "ExternalClient")
        print(self._cmdInjMngr)
        return self._cmdInjMngr
    
    def getTcInjectMngr(self):
        return self._cmdInjMngr
            

        
     
      