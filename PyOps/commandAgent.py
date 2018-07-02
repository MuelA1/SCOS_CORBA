#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Access to SCOS-2000 commanding system

CommandAgent -- describes access to command injection services and command callback creation
"""

from baseAgent import BaseAgent
import ITC_INJ

class CommandAgent(BaseAgent):
       
    def __init__(self):
        super().__init__()
        self.__namingService = 'TC_INJ_002'
        self.__serverMngrType = ITC_INJ.TCinjectServerMngr
        self.__cmdInjMngrView = None
        self.__cmdInjMngr = None
                        
    def getNamingService(self):
        return self.__namingService   
     
    def getServerMngrType(self):
        return self.__serverMngrType
    
    def createCmdInjMngrView(self, cmdView):
        self.__cmdInjMngrView = self.createCorbaObject(cmdView)
            
    def getCmdInjMngrView(self):
        return self.__cmdInjMngrView
    
    def tcInjectMngr(self):
        self.__cmdInjMngr = self._serverMngr.getTCinjectMngr(self.__cmdInjMngrView, "ExternalClient")
          
    def getCmdInjMngr(self):
        return self.__cmdInjMngr
                            