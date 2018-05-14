#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Access to SCOS-2000 TM Parameter Data 

TMParamAgent -- describes access to telemetry parameter services
"""

from BaseAgent import BaseAgent
import ITM_PRO

class TMParamAgent(BaseAgent):
       
    def __init__(self):
        super().__init__()
        self.__namingService = 'TM_PRO_001'
        self.__serverMngrType = ITM_PRO.TMserverMngr
        self.__paramView = None
        self.__tmServerType = None
        self.__paramMngr = None 
        self.__paramSetMngr = None
        
    def getNamingService(self):
        return self.__namingService   
     
    def getServerMngrType(self):
        return self.__serverMngrType
    
    def createParamView(self, paramView, idString):
        self.__paramView = self.createCorbaObject(paramView, idString)
        return self.__paramView
        
    def getParamView(self):
        return self.__paramView
    
    def tmServerType(self):
        self.__tmServerType = self._serverMngr.getTMserver(1)
          
    def getTmServerType(self):
        return self.__tmServerType
    
    def singleTMParamMngr(self):
        self.__paramMngr = self.__tmServerType.m_parameterMngr
          
    def getSingleTMParamMngr(self):
        return self.__paramMngr
    
    def tmParamSetMngr(self):
        self.__paramSetMngr = self.__tmServerType.m_setMngr
          
    def getTMParamSetMngr(self):
        return self.__paramSetMngr