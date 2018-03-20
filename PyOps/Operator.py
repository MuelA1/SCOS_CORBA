#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Facade, higher-level interface to use different agents and to perform specific tasks

"""

from MIBAgent import MIBAgent
from CommandAgent import CommandAgent
from Command import Command

class Operator():
    
    # create Agent Objects
    def __init__(self):
        self.__mibAgent = MIBAgent()
        self.__cmdAgent = CommandAgent()
        self.__command = Command()
        
        self.__cmdInjMngr = None
               
    # perform Agent operations
    def connect(self,ip,port):
        mibMngr = self.__mibAgent.connect(ip,port,self.__mibAgent.getNamingService(),self.__mibAgent.getServerMngrType())
        cmdServerMngr = self.__cmdAgent.connect(ip,port,self.__cmdAgent.getNamingService(),self.__cmdAgent.getServerMngrType())
        return [mibMngr,cmdServerMngr]
    
    def createViewInterfaces(self):
        self.__cmdAgent.createCmdInjMngrView()
        
    def getManagers(self):
        commandDefIterator = self.__mibAgent.commandDefinitionIterator()
        self.__cmdInjMngr = self.__cmdAgent.tcInjectMngr()
        return [commandDefIterator,self.__cmdInjMngr]   
    
    def createCommand(self,cmdName):
        self.setDefaultCommandValues(cmdName)
    
    def setDefaultCommandValues(self,cmdName):
        # default MIB values
        cmdDef = self.__mibAgent.commandDefinition(cmdName)        
        # Test
        print('Original command values from MIB:')
        print(str(cmdDef) + '\n')
        
        self.__command.setCommandName(cmdDef.m_name)
        self.__command.setCommandDescription(cmdDef.m_description)
        self.__command.setCommandParameters(cmdDef.m_params) 
        
    def setRequiredParameterValues(self,paramName,paramValue):
        self.__command.setRequiredParameterValues(paramName,paramValue) 
               
    def injectCommand(self):
        self.__command.injectCommand(self.__cmdInjMngr)