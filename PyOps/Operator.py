#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Facade, higher-level interface to use different agents and to perform specific tasks

Operator -- describes an interface where every object is created
"""

from MIBAgent import MIBAgent
from CommandAgent import CommandAgent
from Command import Command
from ViewInterfaces import CommandInjectMngrView

class Operator():
    
    # create agent objects
    def __init__(self):
        self.__mibAgent = MIBAgent()
        self.__cmdAgent = CommandAgent()
                      
    # perform agent operations
    def connect(self,ip,port):
        mibMngr = self.__mibAgent.connect(ip,port,self.__mibAgent.getNamingService(),self.__mibAgent.getServerMngrType())
        cmdServerMngr = self.__cmdAgent.connect(ip,port,self.__cmdAgent.getNamingService(),self.__cmdAgent.getServerMngrType())
        
        return [mibMngr,cmdServerMngr]
    
    def initialize(self):
        cmdInjMngrView = self.createViewInterfaces()
        [commandDefIterator,cmdInjMngr] = self.getManagers()
    
        return cmdInjMngrView,commandDefIterator,cmdInjMngr
    
    def createViewInterfaces(self):       
        cmdInjMngrView = self.__cmdAgent.createCmdInjMngrView(CommandInjectMngrView(),'MngrView')               
        
        return cmdInjMngrView
    
    def getManagers(self):
        commandDefIterator = self.__mibAgent.commandDefinitionIterator()
        cmdInjMngr = self.__cmdAgent.tcInjectMngr()
        
        return commandDefIterator,cmdInjMngr 
                
    def createCommand(self,cmdName,**cmdKwargs):

        # default MIB values
        cmdDef = self.__mibAgent.commandDefinition(cmdName)        
        # Test
        # print('Original command values from MIB: ' + str(cmdDef))
        
        command = Command(cmdDef.m_name,cmdDef.m_description,**cmdKwargs)              
        command.setCommandDef(cmdDef)
        command.setMIBCommandParameters() 
        command.setCommandInjMngr(self.__cmdAgent.getCmdInjMngr())
        
        return command
        