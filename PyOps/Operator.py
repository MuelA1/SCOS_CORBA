#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Facade, higher-level interface to use different agents and to perform specific tasks

"""

from MIBAgent import MIBAgent
from CommandAgent import CommandAgent

class Operator():
    
    # create Agent Objects
    def __init__(self):
        self.__mibAgent = MIBAgent()
        self.__cmdAgent = CommandAgent()
               
    # perform Agent operations
    def connect(self):
        mibMngr = self.__mibAgent.connect(self.__mibAgent.getNamingService(),self.__mibAgent.getServerMngrType())
        cmdServerMngr = self.__cmdAgent.connect(self.__cmdAgent.getNamingService(),self.__cmdAgent.getServerMngrType())
        return [mibMngr,cmdServerMngr]
    
    def createViewInterfaces(self):
        self.__cmdAgent.createCmdInjMngrView()
        
    def getManagers(self):
        commandDefIterator = self.__mibAgent.commandDefinitionIterator()
        cmdInjMngr = self.__cmdAgent.tcInjectMngr()
        return [commandDefIterator,cmdInjMngr]   
    
    def setDefaultCommandValues(self,cmdName):
        # default MIB values
        cmdDef = self.__mibAgent.commandDefinition(cmdName)        
        # Test
        print('Original command values from MIB:')
        print(str(cmdDef) + '\n')
        
        self.__cmdAgent.setCommandName(cmdDef.m_name)
        self.__cmdAgent.setCommandDescription(cmdDef.m_description)
        self.__cmdAgent.setCommandParameters(cmdDef.m_params) 
        
    def setRequiredParameterValues(self,paramName,paramValue):
        self.__cmdAgent.setRequiredParameterValues(paramName,paramValue) 
               
    def injectCommand(self):
        self.__cmdAgent.injectCommand()