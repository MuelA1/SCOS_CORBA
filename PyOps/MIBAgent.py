#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Access to static data for commands, access to telemetry parameter data 

MIBAgent -- describes MIB access
"""

from BaseAgent import BaseAgent
import IMIB_PRO

class MIBAgent(BaseAgent):
        
    def __init__(self):
        super().__init__()
        self.__namingService = 'MIB_PRO_001'
        self.__serverMngrType = IMIB_PRO.MIBmngr
        self.__commandDefIterator = None
        self.__paramDefIterator = None
           
    def getNamingService(self):
        return self.__namingService   
     
    def getServerMngrType(self):
        return self.__serverMngrType    
    
    def commandDefinitionIterator(self):
        self.__commandDefIterator = self._serverMngr.getCommandDefIterator()

    def commandMIBDefinition(self, command):
        return self.__commandDefIterator.getDef(command)
    
    def parameterDefinitionIterator(self):
        self.__paramDefIterator = self._serverMngr.getParamDefIterator()
     
    def parameterMIBDefinition(self, parameter):
        return self.__paramDefIterator.getDef(parameter)
    